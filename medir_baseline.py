import sqlite3
import time
import os
import platform

DB_NAME = "enem_2025.db"

# RECOMENDAÇÃO DE ITERAÇÕES:
# Como se trata de agregação analítica pesada sobre milhares/milhões de linhas,
# rodar 1000 vezes pode levar de 30 a 60 minutos dependendo da CPU.
# Sugestão: defina 100 para um teste inicial ou 1000 se sua máquina for muito rápida.
N_EXECUCOES = 1000

QUERY_OPERACAO_QUE_DOI = """
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
"""

def obter_metadados():
    if not os.path.exists(DB_NAME):
        raise FileNotFoundError(f"Arquivo '{DB_NAME}' não encontrado no diretório atual.")
    
    tamanho_bytes = os.path.getsize(DB_NAME)
    tamanho_mb = tamanho_bytes / (1024 * 1024)
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM resultados_enem;")
    total_linhas = cur.fetchone()[0]
    conn.close()
    
    return {
        "so": f"{platform.system()} {platform.release()}",
        "cpu": platform.processor() or platform.machine(),
        "tamanho_mb": round(tamanho_mb, 2),
        "total_linhas": total_linhas
    }

def executar_medicao():
    print("=" * 65)
    print("PROJETO N2 - MEDIÇÃO DE BASELINE (SEMANA 1)")
    print("=" * 65)
    
    meta = obter_metadados()
    print(f"Sistema Operacional : {meta['so']}")
    print(f"Processador         : {meta['cpu']}")
    print(f"Base de Dados       : {DB_NAME} ({meta['tamanho_mb']} MB)")
    print(f"Volume Analisado    : {meta['total_linhas']:,} registros")
    print(f"Número de Amostras  : N = {N_EXECUCOES}")
    print("-" * 65)
    print("Cronometrando a operação analítica (Full Table Scan)...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Aquecimento de 1 ciclo (warm-up) para inicialização de buffers
    cursor.execute(QUERY_OPERACAO_QUE_DOI)
    _ = cursor.fetchall()

    # Laço oficial de medição com time.perf_counter (alta precisão)
    inicio = time.perf_counter()
    for i in range(1, N_EXECUCOES + 1):
        cursor.execute(QUERY_OPERACAO_QUE_DOI)
        _ = cursor.fetchall()
        
        # Feedback visual de progresso
        if i % (max(1, N_EXECUCOES // 10)) == 0:
            print(f"  -> Progresso: {i}/{N_EXECUCOES} iterações concluídas...")
            
    fim = time.perf_counter()
    conn.close()

    tempo_total = fim - inicio
    tempo_medio_segundos = tempo_total / N_EXECUCOES
    tempo_medio_ms = tempo_medio_segundos * 1000

    print("=" * 65)
    print("RESULTADO OFICIAL DO BASELINE:")
    print(f"Tempo Total        : {tempo_total:.4f} s")
    print(f"Tempo Médio        : {tempo_medio_ms:.2f} ms por operação")
    print(f"Iterações (N)      : {N_EXECUCOES}")
    print("=" * 65)

    # Gravação do relatório técnico para a entrega
    with open("baseline_dados.txt", "w", encoding="utf-8") as f:
        f.write("RELATÓRIO TÉCNICO DE BASELINE - SEMANA 1\n")
        f.write("-" * 40 + "\n")
        f.write(f"Sistema: Painel Analítico ENEM 2025 (SQLite)\n")
        f.write(f"Operação: Agregação analítica e cálculo de médias por UF (GROUP BY)\n")
        f.write(f"Tamanho dos Dados: {meta['total_linhas']:,} registros ({meta['tamanho_mb']} MB)\n")
        f.write(f"Ambiente: {meta['cpu']} | {meta['so']}\n")
        f.write(f"Amostras (N): {N_EXECUCOES}\n")
        f.write(f"Tempo Total: {tempo_total:.4f} s\n")
        f.write(f"Tempo Médio (Baseline): {tempo_medio_ms:.2f} ms por operação\n")

    print("\nArquivo 'baseline_dados.txt' gerado com sucesso!")

if __name__ == "__main__":
    executar_medicao()