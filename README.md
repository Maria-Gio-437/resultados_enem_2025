# Projeto N2 - Persistência de Dados: Otimização de Desempenho

Este projeto integra a avaliação N2 da disciplina de **Persistência de Dados**. O escopo consiste em avaliar o desempenho inicial (Baseline) de consultas relacionais sobre uma base massiva e, nas fases subsequentes, implementar uma nova camada de persistência para mitigar gargalos e mensurar ganhos computacionais.

---

## 📌 Escopo e Arquitetura Inicial

O software realiza consultas analíticas e pontuais sobre os microdados de resultados do **ENEM 2025**, persistidos localmente em banco relacional **SQLite (`enem_2025.db`)**.

### Funcionalidades do Sistema:
1. **Consulta por Candidato:** Busca pontual por Chave Primária (`ID_RESULTADO`).
2. **Estatísticas por Região:** Consultas analíticas agregadas com agrupamento hierárquico dinâmico.
3. **Top 10 Redações:** Consulta com ordenação descendente e paginação fixa (`LIMIT 10`), com desempate pela nota de Matemática.

---

## 🔍 Como Funcionam os Filtros de Estatística

A aba **"Estatísticas por Região"** possui 4 comportamentos:

* **Se ambos os campos estiverem vazios:** É retornado o geral do Brasil na primeira linha e, abaixo, a média individual de cada um dos estados.
* **Se apenas a UF for preenchida:** É retornado o total daquele estado na primeira linha e, abaixo, a média de cada uma das cidades pertencentes a ele.
* **Se apenas o Município for preenchido:** É retornada a média daquele município (caso existam cidades com o mesmo nome em estados diferentes, cada uma aparece separada com sua respectiva UF).
* **Se a UF e o Município forem preenchidos:** É retornada apenas uma única linha com a média exata daquela cidade naquele estado.

---

## 🗄️ Modelo de Dados (`resultados_enem`)

| Coluna | Tipo SQLite | Descrição |
| :--- | :--- | :--- |
| `ID_RESULTADO` | INTEGER (PK) | Identificador sequencial unívoco da linha |
| `NO_MUNICIPIO_PROVA` | TEXT | Município de aplicação do exame |
| `SG_UF_PROVA` | TEXT | Sigla da Unidade Federativa |
| `NU_NOTA_CN` | REAL | Nota em Ciências da Natureza |
| `NU_NOTA_CH` | REAL | Nota em Ciências Humanas |
| `NU_NOTA_LC` | REAL | Nota em Linguagens e Códigos |
| `NU_NOTA_MT` | REAL | Nota em Matemática |
| `NU_NOTA_REDACAO` | REAL | Nota na Prova de Redação |

---

## 🚀 Instruções de Execução

### Pré-requisitos
* Python 3.10 ou superior instalado.
* Arquivo `enem_2025.db` presente na pasta dados.

### Executando a Aplicação
```bash
python app.py