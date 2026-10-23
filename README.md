# Projeto N2 - Persistência de Dados: Otimização com Camada de Cache (Redis)

Este projeto integra a avaliação N2 da disciplina de **Persistência de Dados (ESW441)** do curso de Engenharia de Software da **UniRV (Universidade de Rio Verde)**.

* **Integrantes do Trio:**
  1. Luiz Eduardo Santos Silva
  2. Henrique Thomaz Landim Ruffato
  3. Maria Giovanna Fernandes Lima
* **Professor:** Gustavo Martins Lima
* **Entrega Final:** 03/11

---

## 📌 Escopo e Arquitetura do Sistema

O sistema é um painel analítico construído em **Python (Tkinter)** sobre os microdados oficiais do **ENEM 2025** (base massiva com mais de 1.048.000 registros). 

A arquitetura adota **persistência poliglota** combinando armazenamento relacional com camada de memória RAM:

1. **Fonte da Verdade (Primary Store - Relacional):**
   * **SQLite (`dados/enem_2025.db`)**: Armazena a totalidade dos registros brutos e garante atomicidade e durabilidade nas operações de escrita.
2. **Camada de Cache em Memória (Key-Value Store):**
   * **Redis (via Docker na porta 6379)**: Armazena os resultados de agregações analíticas pesadas serializados em JSON, eliminando varreduras repetidas em disco (*Full Table Scans*).

```
[ Usuário / Tkinter (app.py) ]
       │
       ├─── 1. Consulta Cache ───► [ Redis (Porta 6379 / Docker) ]
       │                              │
       │                              ├─ HIT ──► Retorno Instantâneo (O(1))
       │                              └─ MISS ─┐
       │                                       ▼
       └─── 2. Consulta / Escrita ──► [ SQLite (dados/enem_2025.db) ]
```

---

## ⚡ Padrão Arquitetural: Cache-Aside

A comunicação com o Redis é intermediada pelo módulo [`cache.py`](cache.py), implementando o padrão **Cache-Aside** (Lazy Loading):

* **Fluxo de Leitura (Agregações Analíticas):**
  1. A aplicação calcula a chave determinística da consulta (ex: `enem:stats:brasil_completo` ou `enem:stats:uf:GO`).
  2. Tenta recuperar o JSON no Redis:
     * **Cache HIT (Verde no Rodapé):** Retorno imediato da memória RAM em sub-milissegundos ($< 1$ ms).
     * **Cache MISS (Vermelho no Rodapé):** O Redis não possui a chave. A consulta é executada no SQLite, o resultado é persistido no Redis com TTL de segurança de 24h (`86400s`) e devolvido à interface.
* **Chaves Determinísticas Padronizadas:**
  * `enem:stats:brasil_completo` (Média consolidada do país e cada estado)
  * `enem:stats:uf:{UF}` (Média do estado e municípios)
  * `enem:stats:mun:{MUNICIPIO_NORMALIZADO}` (Municípios homônimos)
  * `enem:stats:uf:{UF}:mun:{MUNICIPIO_NORMALIZADO}` (Cidade específica)
  * `enem:top10:todas` e `enem:top10:uf:{UF}` (Top 10 melhores redações)

---

## 🔄 Invalidação na Escrita (Consistência de Dados)

Na **Aba 4 ("Corrigir Nota / Invalidação")**, é simulado um recurso formal de aluno que altera a nota de um candidato:

1. **Fonte da Verdade Primeiro:** O sistema executa `UPDATE` e `COMMIT` transacional diretamente no SQLite.
2. **Invalidação Atômica no Redis:** O sistema identifica o estado e município do candidato alterado e dispara o comando `DEL` para invalidar as agregações impactadas:
   * A chave do Brasil (`enem:stats:brasil_completo`)
   * A chave daquele estado (`enem:stats:uf:{UF}`)
   * A chave daquele município (`enem:stats:mun:...`)
   * As chaves do ranking (`enem:top10:...`)
3. **Garantia de Consistência:** A próxima consulta nessas localidades forçará um **Cache MISS**, recalculando as médias consolidadas a partir do SQLite atualizado e regravando o novo valor no Redis.

---

## 📁 Estrutura de Diretórios do Repositório

```text
resultados_enem_2025/
├── app.py                     # Aplicação GUI principal (Tkinter)
├── cache.py                   # Camada de integração Redis (Cache-Aside e Invalidação)
├── docker-compose.yml         # Configuração do container Docker do Redis
├── requirements.txt           # Dependências Python (biblioteca redis)
├── README.md                  # Manual do projeto e guia de execução
├── dados/
│   └── enem_2025.db           # Banco de dados SQLite massivo (> 1 milhão de linhas)
├── benchmark/
│   ├── medir_baseline.py      # Script oficial de medição de latência do Baseline
│   └── baseline_dados.txt     # Relatório textual com as 1.000 iterações aferidas
└── docs/
    ├── relatorio_diagnostico_baseline.md   # Relatório técnico da Semana 1
    └── modelagem_da_camada.pdf            # Documento técnico da Semana 2
```

---

## 🚀 Como Executar o Projeto (Checkpoint Semana 3)

### 1. Pré-requisitos
* **Python 3.10 ou superior** instalado.
* **Docker e Docker Compose** (ou Docker Desktop) instalados e em execução.

---

### 2. Passo a Passo de Execução

#### Passo 1: Subir o Servidor Redis no Docker
Na raiz do repositório, execute:
```bash
docker compose up -d
```
*(Opcional: se preferir usar `docker run` direto sem compose:)*
```bash
docker run -d --name enem_redis -p 6379:6379 --restart unless-stopped redis:7-alpine
```

Para verificar se o container está ativo:
```bash
docker ps
```
Você deverá ver o container `enem_redis` com status *Up* na porta `0.0.0.0:6379->6379/tcp`.

---

#### Passo 2: Instalar as Dependências do Python
Instale os pacotes necessários:
```bash
pip install -r requirements.txt
```

---

#### Passo 3: Executar a Aplicação
Inicie a interface gráfica:
```bash
python app.py
```

---

## 🧪 Roteiro de Validação do Checkpoint (Demonstração)

1. **Validando o Cache-Aside (HIT vs. MISS):**
   * Acesse a aba **"Estatísticas por Região"**.
   * Deixe os campos em branco e clique em **"Calcular Médias"**:
     * **1ª Consulta (MISS):** O rodapé exibirá `SQLITE (MISS)` com tempo em torno de centenas de milissegundos (~700ms a 900ms). Os dados foram lidos do disco e cacheados.
     * **2ª Consulta (HIT):** Clique novamente no mesmo botão. O rodapé mudará imediatamente para `REDIS (HIT)` em verde com tempo inferior a **2 ms** (~0.5ms a 1ms), comprovando o ganho de desempenho em memória RAM.

2. **Validando a Invalidação na Escrita:**
   * Anote a média de um estado (por exemplo, `GO`) na aba **"Estatísticas por Região"**.
   * Vá até a aba **"Corrigir Nota (Invalidação)"**.
   * Digite o ID de um candidato daquele estado (ex: ID `1`) e altere sua nota de redação.
   * Clique em **"Gravar no SQLite e Invalidar Cache"**.
   * O sistema gravará no SQLite e executará `DEL` nas chaves do Redis.
   * Volte à aba de **"Estatísticas por Região"** e pesquise por `GO`: a consulta dará `SQLITE (MISS)`, demonstrando que o cache anterior foi descartado e a nova média recalculada com precisão.

3. **Tolerância a Falhas (Fallback Gracioso):**
   * Caso o Docker/Redis esteja desligado, a aplicação **não quebra**: ela detecta a ausência do cache e funciona normalmente em modo relacional direto (`SQLITE (SEM CACHE)`).