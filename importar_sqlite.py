import sqlite3
import pandas as pd

ARQUIVO_DADOS = "RESULTADOS_ENEM_2025.csv"
NOME_BANCO = "enem_2025.db"
TAMANHO_LOTE = 100_000

conn = sqlite3.connect(NOME_BANCO)
cursor = conn.cursor()
cursor.execute("PRAGMA synchronous = OFF;")
cursor.execute("PRAGMA journal_mode = MEMORY;")
cursor.execute("""
CREATE TABLE IF NOT EXISTS resultados_enem (
    ID_RESULTADO INTEGER PRIMARY KEY,
    NO_MUNICIPIO_PROVA TEXT,
    SG_UF_PROVA TEXT,
    NU_NOTA_CN REAL,
    NU_NOTA_CH REAL,
    NU_NOTA_LC REAL,
    NU_NOTA_MT REAL,
    NU_NOTA_REDACAO REAL
);
""")
conn.commit()

print("Iniciando a importação dos dados...")

total_inserido = 0

leitor = pd.read_csv(
    ARQUIVO_DADOS,
    sep=";",               
    encoding="latin1",     
    chunksize=TAMANHO_LOTE,
    dtype={
        "ID_RESULTADO": "int64",
        "NO_MUNICIPIO_PROVA": "string",
        "SG_UF_PROVA": "string",
        "NU_NOTA_CN": "float64",
        "NU_NOTA_CH": "float64",
        "NU_NOTA_LC": "float64",
        "NU_NOTA_MT": "float64",
        "NU_NOTA_REDACAO": "float64"
    }
)

for i, chunk in enumerate(leitor):
    # Converte valores ausentes para None (que vira NULL no SQLite)
    chunk = chunk.where(pd.notnull(chunk), None)
    chunk.to_sql("resultados_enem", conn, if_exists="append", index=False)
    
    total_inserido += len(chunk)
    print(f"Lote {i + 1} processado. Total de registros: {total_inserido:,}")

cursor.execute("PRAGMA synchronous = NORMAL;")
conn.commit()
conn.close()

print(f"\nImportação concluída com sucesso! Banco '{NOME_BANCO}' criado com {total_inserido:,} registros.")