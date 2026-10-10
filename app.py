import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "enem_2025.db"

def get_db_connection():
    return sqlite3.connect(DB_NAME)

class EnemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Análise - Microdados ENEM 2025")
        self.root.geometry("980x640")
        self.root.minsize(800, 520)

        # Container de Abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Abas
        self.tab_candidato = ttk.Frame(self.notebook)
        self.tab_estatisticas = ttk.Frame(self.notebook)
        self.tab_top10 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_candidato, text="Consulta por Candidato")
        self.notebook.add(self.tab_estatisticas, text="Estatísticas por Região")
        self.notebook.add(self.tab_top10, text="Top 10 Redações")

        self.setup_tab_candidato()
        self.setup_tab_estatisticas()
        self.setup_tab_top10()

    # -------------------------------------------------------------
    # ABA 1: CONSULTA POR CANDIDATO
    # -------------------------------------------------------------
    def setup_tab_candidato(self):
        frame_busca = ttk.LabelFrame(self.tab_candidato, text="Buscar Registro")
        frame_busca.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_busca, text="ID Resultado:").pack(side="left", padx=5, pady=5)
        self.entry_id = ttk.Entry(frame_busca, width=20)
        self.entry_id.pack(side="left", padx=5, pady=5)

        btn_buscar = ttk.Button(frame_busca, text="Buscar", command=self.buscar_candidato)
        btn_buscar.pack(side="left", padx=10, pady=5)

        colunas = ("id", "municipio", "uf", "cn", "ch", "lc", "mt", "redacao")
        self.tree_candidato = ttk.Treeview(self.tab_candidato, columns=colunas, show="headings", height=5)
        self.tree_candidato.pack(fill="both", expand=True, padx=10, pady=10)

        titulos = [
            ("id", "ID", 90),
            ("municipio", "Município", 200),
            ("uf", "UF", 50),
            ("cn", "Ciências Nat.", 100),
            ("ch", "Ciências Hum.", 100),
            ("lc", "Linguagens", 100),
            ("mt", "Matemática", 100),
            ("redacao", "Redação", 100),
        ]
        for col, titulo, largura in titulos:
            self.tree_candidato.heading(col, text=titulo)
            self.tree_candidato.column(col, width=largura, anchor="center")

    def buscar_candidato(self):
        id_resultado = self.entry_id.get().strip()
        if not id_resultado.isdigit():
            messagebox.showwarning("Aviso", "Informe um ID numérico válido.")
            return

        for row in self.tree_candidato.get_children():
            self.tree_candidato.delete(row)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID_RESULTADO, NO_MUNICIPIO_PROVA, SG_UF_PROVA, 
                   NU_NOTA_CN, NU_NOTA_CH, NU_NOTA_LC, NU_NOTA_MT, NU_NOTA_REDACAO
            FROM resultados_enem
            WHERE ID_RESULTADO = ?
        """, (int(id_resultado),))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            dados_formatados = [val if val is not None else "-" for val in resultado]
            self.tree_candidato.insert("", "end", values=dados_formatados)
        else:
            messagebox.showinfo("Busca", "Nenhum candidato encontrado com este ID.")

    # -------------------------------------------------------------
    # ABA 2: ESTATÍSTICAS POR ESTADO E MUNICÍPIO (HIERÁRQUICA)
    # -------------------------------------------------------------
    def setup_tab_estatisticas(self):
        frame_filtros = ttk.LabelFrame(self.tab_estatisticas, text="Filtros de Agregação")
        frame_filtros.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_filtros, text="UF (ex: GO):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_uf = ttk.Entry(frame_filtros, width=6)
        self.entry_uf.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_filtros, text="Município:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_municipio = ttk.Entry(frame_filtros, width=25)
        self.entry_municipio.grid(row=0, column=3, padx=5, pady=5)

        btn_calcular = ttk.Button(frame_filtros, text="Calcular Médias", command=self.calcular_estatisticas)
        btn_calcular.grid(row=0, column=4, padx=10, pady=5)

        # Container com Tabela e Barra de Rolagem Vertical
        frame_tabela = ttk.Frame(self.tab_estatisticas)
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        colunas = ("local", "total", "media_cn", "media_ch", "media_lc", "media_mt", "media_redacao")
        self.tree_stats = ttk.Treeview(
            frame_tabela, 
            columns=colunas, 
            show="headings", 
            yscrollcommand=scrollbar.set
        )
        self.tree_stats.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree_stats.yview)

        titulos = [
            ("local", "Abrangência / Localidade", 250),
            ("total", "Participantes", 110),
            ("media_cn", "Média CN", 95),
            ("media_ch", "Média CH", 95),
            ("media_lc", "Média LC", 95),
            ("media_mt", "Média MT", 95),
            ("media_redacao", "Média Redação", 105),
        ]
        for col, titulo, largura in titulos:
            self.tree_stats.heading(col, text=titulo)
            self.tree_stats.column(col, width=largura, anchor="center")

    def calcular_estatisticas(self):
        uf = self.entry_uf.get().strip().upper()
        municipio = self.entry_municipio.get().strip()

        for row in self.tree_stats.get_children():
            self.tree_stats.delete(row)

        conn = get_db_connection()
        cursor = conn.cursor()

        # CENÁRIO 1: Ambos os campos vazios -> Brasil (Geral) + Cada Estado
        if not uf and not municipio:
            # Total Geral Brasil
            cursor.execute("""
                SELECT 
                    COUNT(*),
                    ROUND(AVG(NU_NOTA_CN), 2),
                    ROUND(AVG(NU_NOTA_CH), 2),
                    ROUND(AVG(NU_NOTA_LC), 2),
                    ROUND(AVG(NU_NOTA_MT), 2),
                    ROUND(AVG(NU_NOTA_REDACAO), 2)
                FROM resultados_enem
            """)
            brasil = cursor.fetchone()
            if brasil and brasil[0] > 0:
                self.tree_stats.insert("", "end", values=[
                    "BRASIL (CONSOLIDADO)", f"{brasil[0]:,}"
                ] + [v if v is not None else "-" for v in brasil[1:]])

            # Média por Estado
            cursor.execute("""
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
                ORDER BY SG_UF_PROVA ASC
            """)
            for estado in cursor.fetchall():
                self.tree_stats.insert("", "end", values=[
                    f"Estado: {estado[0]}", f"{estado[1]:,}"
                ] + [v if v is not None else "-" for v in estado[2:]])

        # CENÁRIO 2: Apenas UF informada -> Média do Estado + Cidades do Estado
        elif uf and not municipio:
            # Consolidado do Estado
            cursor.execute("""
                SELECT 
                    COUNT(*),
                    ROUND(AVG(NU_NOTA_CN), 2),
                    ROUND(AVG(NU_NOTA_CH), 2),
                    ROUND(AVG(NU_NOTA_LC), 2),
                    ROUND(AVG(NU_NOTA_MT), 2),
                    ROUND(AVG(NU_NOTA_REDACAO), 2)
                FROM resultados_enem
                WHERE SG_UF_PROVA = ?
            """, (uf,))
            estado_consolidado = cursor.fetchone()

            if not estado_consolidado or estado_consolidado[0] == 0:
                conn.close()
                messagebox.showinfo("Estatísticas", f"Nenhum dado encontrado para a UF '{uf}'.")
                return

            self.tree_stats.insert("", "end", values=[
                f"ESTADO {uf} (CONSOLIDADO)", f"{estado_consolidado[0]:,}"
            ] + [v if v is not None else "-" for v in estado_consolidado[1:]])

            # Cidades daquele Estado
            cursor.execute("""
                SELECT 
                    NO_MUNICIPIO_PROVA,
                    COUNT(*),
                    ROUND(AVG(NU_NOTA_CN), 2),
                    ROUND(AVG(NU_NOTA_CH), 2),
                    ROUND(AVG(NU_NOTA_LC), 2),
                    ROUND(AVG(NU_NOTA_MT), 2),
                    ROUND(AVG(NU_NOTA_REDACAO), 2)
                FROM resultados_enem
                WHERE SG_UF_PROVA = ? AND NO_MUNICIPIO_PROVA IS NOT NULL
                GROUP BY NO_MUNICIPIO_PROVA
                ORDER BY NO_MUNICIPIO_PROVA ASC
            """, (uf,))
            for cidade in cursor.fetchall():
                self.tree_stats.insert("", "end", values=[
                    f"{cidade[0]} ({uf})", f"{cidade[1]:,}"
                ] + [v if v is not None else "-" for v in cidade[2:]])

        # CENÁRIO 3: Apenas Município informado -> Cidades homônimas diferenciadas por UF
        elif not uf and municipio:
            cursor.execute("""
                SELECT 
                    NO_MUNICIPIO_PROVA,
                    SG_UF_PROVA,
                    COUNT(*),
                    ROUND(AVG(NU_NOTA_CN), 2),
                    ROUND(AVG(NU_NOTA_CH), 2),
                    ROUND(AVG(NU_NOTA_LC), 2),
                    ROUND(AVG(NU_NOTA_MT), 2),
                    ROUND(AVG(NU_NOTA_REDACAO), 2)
                FROM resultados_enem
                WHERE UPPER(NO_MUNICIPIO_PROVA) = UPPER(?)
                GROUP BY NO_MUNICIPIO_PROVA, SG_UF_PROVA
                ORDER BY SG_UF_PROVA ASC
            """, (municipio,))
            cidades = cursor.fetchall()

            if not cidades:
                conn.close()
                messagebox.showinfo("Estatísticas", f"Nenhum dado localizado para o município '{municipio}'.")
                return

            for cid in cidades:
                self.tree_stats.insert("", "end", values=[
                    f"{cid[0]} - {cid[1]}", f"{cid[2]:,}"
                ] + [v if v is not None else "-" for v in cid[3:]])

        # CENÁRIO 4: UF e Município informados -> Linha única exata
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*),
                    ROUND(AVG(NU_NOTA_CN), 2),
                    ROUND(AVG(NU_NOTA_CH), 2),
                    ROUND(AVG(NU_NOTA_LC), 2),
                    ROUND(AVG(NU_NOTA_MT), 2),
                    ROUND(AVG(NU_NOTA_REDACAO), 2)
                FROM resultados_enem
                WHERE SG_UF_PROVA = ? AND UPPER(NO_MUNICIPIO_PROVA) = UPPER(?)
            """, (uf, municipio))
            res = cursor.fetchone()

            if not res or res[0] == 0:
                conn.close()
                messagebox.showinfo("Estatísticas", f"Nenhum registro para {municipio} em {uf}.")
                return

            self.tree_stats.insert("", "end", values=[
                f"{municipio} - {uf}", f"{res[0]:,}"
            ] + [v if v is not None else "-" for v in res[1:]])

        conn.close()

    # -------------------------------------------------------------
    # ABA 3: TOP 10 REDAÇÕES
    # -------------------------------------------------------------
    def setup_tab_top10(self):
        frame_filtros_top = ttk.LabelFrame(self.tab_top10, text="Filtros de Busca")
        frame_filtros_top.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_filtros_top, text="Filtrar por UF (Opcional):").pack(side="left", padx=5, pady=5)
        self.entry_top_uf = ttk.Entry(frame_filtros_top, width=6)
        self.entry_top_uf.pack(side="left", padx=5, pady=5)

        btn_top10 = ttk.Button(frame_filtros_top, text="Listar Top 10", command=self.listar_top10)
        btn_top10.pack(side="left", padx=10, pady=5)

        colunas = ("posicao", "id", "municipio", "uf", "redacao", "mt")
        self.tree_top10 = ttk.Treeview(self.tab_top10, columns=colunas, show="headings", height=12)
        self.tree_top10.pack(fill="both", expand=True, padx=10, pady=10)

        titulos = [
            ("posicao", "Posição", 65),
            ("id", "ID Resultado", 110),
            ("municipio", "Município", 220),
            ("uf", "UF", 55),
            ("redacao", "Nota Redação", 105),
            ("mt", "Nota Matemática", 105),
        ]
        for col, titulo, largura in titulos:
            self.tree_top10.heading(col, text=titulo)
            self.tree_top10.column(col, width=largura, anchor="center")

    def listar_top10(self):
        uf = self.entry_top_uf.get().strip().upper()

        for row in self.tree_top10.get_children():
            self.tree_top10.delete(row)

        query = """
            SELECT ID_RESULTADO, NO_MUNICIPIO_PROVA, SG_UF_PROVA, NU_NOTA_REDACAO, NU_NOTA_MT
            FROM resultados_enem
            WHERE NU_NOTA_REDACAO IS NOT NULL
        """
        params = []

        if uf:
            query += " AND SG_UF_PROVA = ?"
            params.append(uf)

        query += " ORDER BY NU_NOTA_REDACAO DESC, NU_NOTA_MT DESC LIMIT 10"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()

        if resultados:
            for idx, res in enumerate(resultados, 1):
                linha = [f"{idx}º", res[0], res[1], res[2], res[3], res[4] if res[4] is not None else "-"]
                self.tree_top10.insert("", "end", values=linha)
        else:
            messagebox.showinfo("Top 10", "Nenhum resultado localizado.")

if __name__ == "__main__":
    root = tk.Tk()
    app = EnemApp(root)
    root.mainloop()