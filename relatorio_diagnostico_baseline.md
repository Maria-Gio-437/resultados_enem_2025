# PROJETO N2 - PERSISTÊNCIA DE DADOS (ESW441)
## SEMANA 1: DIAGNÓSTICO E BASELINE

---

### 1. DADOS DE IDENTIFICAÇÃO

* **Instituição:** Universidade de Rio Verde (UniRV)
* **Curso:** Engenharia de Software
* **Disciplina:** ESW441 - Persistência de Dados
* **Professor:** Gustavo Martins Lima
* **Integrantes do Trio:**
  1. Luiz Eduardo Santos Silva
  2. Henrique Thomaz Landim Ruffato
  3. Maria Giovanna Fernandes Lima
* **Sistema Escolhido:** Painel Analítico de Microdados do ENEM 2025 (Python / Tkinter / SQLite)

---

### 2. PONTO DE DOR DO SISTEMA

> *"Hoje o sistema realiza varreduras completas em disco (Full Table Scan) no banco relacional SQLite a cada consulta analítica ou de agregação (como médias consolidadas por estado e município), e isso é lento porque recalcula operações pesadas sobre mais de 1 milhão de linhas repetidamente sem nenhuma camada de reaproveitamento em memória."*

---

### 3. HIPÓTESE TÉCNICA DE PERSISTÊNCIA (CAMINHO ESCOLHIDO)

* **Tecnologia Proposta:** **Redis** (Banco Não-Relacional Chave-Valor em Memória RAM / Estrutura de Cache).
* **Fundamentação Técnica da Hipótese:**  
  A base de dados do ENEM possui natureza puramente analítica e imutável (*append-only* ou somente leitura após a ingestão inicial). Consequentemente, as agregações mais custosas e demandadas pela interface (como médias gerais por estado e por município) produzem exatamente o mesmo resultado a cada execução.
  
  A hipótese do projeto é que a implementação de uma camada de persistência em memória via **Redis**, estruturada sob o padrão arquitetural *Cache-Aside*, eliminará os gargalos de I/O em disco e os *Full Table Scans* recorrentes no SQLite. Os resultados agregados pré-calculados serão serializados em JSON e associados a chaves determinísticas (ex: `stats:uf:todas`, `stats:uf:{sigla}`).
  
  Com isso, a complexidade temporal da leitura passará de uma varredura custosa em disco para uma recuperação com complexidade $O(1)$ na memória RAM, projetando uma redução drástica do tempo de resposta: saindo da casa de centenas de milissegundos para sub-milissegundos e desonerando o banco relacional principal.

---

### 4. METODOLOGIA DE MEDIÇÃO DO BASELINE

* **Operação Analisada:** Consulta de agregação analítica completa com agrupamento por Unidade Federativa (`GROUP BY SG_UF_PROVA`), contagem de registros e cálculo de médias aritméticas de 5 competências (`NU_NOTA_CN`, `NU_NOTA_CH`, `NU_NOTA_LC`, `NU_NOTA_MT`, `NU_NOTA_REDACAO`).
* **Sentença SQL Submetida ao Benchmark:**
  ```sql
  SELECT 
      SG_UF_PROVA,
      COUNT(*),
      ROUND(AVG(NU_NOTA_CN), 2),
      ROUND(AVG(NU_NOTA_CH), 2),
      ROUND(AVG(NU_NOTA_LC), 2),
      ROUND(AVG(NU_NOTA_MT), 2),
      ROUND(AVG(NU_NOTA_REDACAO), 2)
  FROM resultados_enem
  WHERE SG_UF_PROVA IS NOT NULL
  GROUP BY SG_UF_PROVA
  ORDER BY SG_UF_PROVA ASC;
  ```
* **Protocolo Experimental de Medição:**
  1. **Isolamento de Ambiente:** Utilização do script padronizado `medir_baseline.py` rodando sobre o arquivo de banco de produção local (`enem_2025.db`).
  2. **Ciclo de Warm-up:** Execução prévia de 1 iteração não cronometrada para alocação de ponteiros e aquecimento de buffers de leitura do SO/SQLite.
  3. **Amostragem em Lote:** Execução contínua de um laço fechado de $N = 1000$ iterações utilizando `time.perf_counter()` para cronometragem com resolução de nanossegundos.
  4. **Cálculo Estatístico do Baseline:**
     $$\text{Tempo Médio} = \frac{\text{Tempo Total}}{N}$$

---

### 5. FICHA TÉCNICA E RESULTADOS DO BASELINE ("ANTES")

| Métrica / Parâmetro | Especificação / Valor Aferido |
| :--- | :--- |
| **Volume de Registros Analisados** | **1.048.575 linhas** |
| **Tamanho Físico da Base em Disco** | **56,34 MB** (`enem_2025.db`) |
| **Processador / Arquitetura** | AMD64 Family 25 Model 80 Stepping 0 (AuthenticAMD) |
| **Sistema Operacional** | Windows 11 |
| **Tamanho da Amostra ($N$)** | **1.000 iterações** |
| **Tempo Total Cronometrado** | **788,6199 s** (~13 minutos e 08 segundos) |
| **BASELINE MÉDIO ("ANTES")** | **788,62 ms por operação** |

---

### 6. ARTEFATOS DO REPOSITÓRIO

* `medir_baseline.py`: Script Python oficial responsável pela coleta de metadados, execução do benchmark de $N=1000$ iterações e cálculo estatístico.
* `baseline_dados.txt`: Arquivo de saída gerado pelo script contendo o log formal da medição em disco.
* `app.py`: Interface gráfica e lógica atual de consultas em SQLite (antes da integração com o Redis).
* `importar_sqlite.py`: Pipeline de ingestão em lotes responsável pela carga de microdados na base relacional.