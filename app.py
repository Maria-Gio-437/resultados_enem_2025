import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "enem_2025.db"
COR_PRIMARIA = "#2b3980"  # Azul escuro
COR_BRANCO = "#ffffff"    # Branco
COR_FUNDO = "#f4f6fa"     # Cinza-azulado muito suave para contraste visual
COR_HOVER = "#1f2a63"     # Azul sutilmente mais escuro para foco

def get_db_connection():
    return sqlite3.connect(DB_NAME)

class EnemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Análise - Microdados ENEM 2025")
        largura = 1000
        altura = 650
        self.centralizar_janela(largura, altura)
        self.root.minsize(820, 540)
        self.root.configure(bg=COR_FUNDO)
        self.configurar_estilos()

        # Container Principal
        container = tk.Frame(self.root, bg=COR_FUNDO)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Cabeçalho Superior
        header = tk.Frame(container, bg=COR_PRIMARIA, height=50)
        header.pack(fill="x", pady=(0, 10))
        lbl_titulo = tk.Label(
            header,
            text="SISTEMA DE ANÁLISE ENEM 2025",
            bg=COR_PRIMARIA,
            fg=COR_BRANCO,
            font=("Segoe UI", 13, "bold"),
            pady=10
        )
        lbl_titulo.pack()

        # Container de Abas
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        # Criação das Abas
        self.tab_candidato = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.tab_estatisticas = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.tab_top10 = ttk.Frame(self.notebook, style="Custom.TFrame")

        self.notebook.add(self.tab_candidato, text="  Consulta por Candidato  ")
        self.notebook.add(self.tab_estatisticas, text="  Estatísticas por Região  ")
        self.notebook.add(self.tab_top10, text="  Top 10 Redações  ")

        # Inicialização das telas
        self.setup_tab_candidato()
        self.setup_tab_estatisticas()
        self.setup_tab_top10()

    def centralizar_janela(self, largura, altura):
        self.root.update_idletasks()
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela - largura) // 2
        pos_y = (altura_tela - altura) // 2
        self.root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Frames
        style.configure("Custom.TFrame", background=COR_FUNDO)
        style.configure("TLabelframe", background=COR_FUNDO, bordercolor="#d0d5dd")
        style.configure("TLabelframe.Label", background=COR_FUNDO, foreground=COR_PRIMARIA, font=("Segoe UI", 9, "bold"))

        # Abas (Notebook)
        style.configure(
            "TNotebook",
            background=COR_FUNDO,
            borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            background="#dbe1f1",
            foreground=COR_PRIMARIA,
            font=("Segoe UI", 9, "bold"),
            padding=[14, 6]
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COR_PRIMARIA)],
            foreground=[("selected", COR_BRANCO)]
        )

        # Botão com visual arredondado/suave
        style.configure(
            "Rounded.TButton",
            background=COR_PRIMARIA,
            foreground=COR_BRANCO,
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            focusthickness=3,
            focuscolor="none",
            padding=[14, 6]
        )
        style.map(
            "Rounded.TButton",
            background=[("active", COR_HOVER), ("pressed", "#151c42")],
            foreground=[("active", COR_BRANCO)]
        )

        # Entradas de Texto (Entry)
        style.configure(
            "TEntry",
            fieldbackground=COR_BRANCO,
            foreground="#222222",
            padding=4
        )

        # Tabelas (Treeview)
        style.configure(
            "Treeview",
            background=COR_BRANCO,
            foreground="#222222",
            fieldbackground=COR_BRANCO,
            rowheight=26,
            font=("Segoe UI", 9),
            borderwidth=0
        )
        style.map(
            "Treeview",
            background=[("selected", COR_PRIMARIA)],
            foreground=[("selected", COR_BRANCO)]
        )
        style.configure(
            "Treeview.Heading",
            background=COR_PRIMARIA,
            foreground=COR_BRANCO,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=[4, 6]
        )
        style.map(
            "Treeview.Heading",
            background=[("active", COR_HOVER)],
            foreground=[("active", COR_BRANCO)]
        )

    # -------------------------------------------------------------
    # ABA 1: CONSULTA POR CANDIDATO
    # -------------------------------------------------------------
    def setup_tab_candidato(self):
        frame_busca = ttk.LabelFrame(self.tab_candidato, text=" Buscar Candidato ")
        frame_busca.pack(fill="x", padx=15, pady=12)

        ttk.Label(frame_busca, text="ID Resultado:", background=COR_FUNDO, font=("Segoe UI", 9)).pack(side="left", padx=8, pady=8)
        self.entry_id = ttk.Entry(frame_busca, width=20)
        self.entry_id.pack(side="left", padx=5, pady=8)

        btn_buscar = ttk.Button(frame_busca, text="Buscar", style="Rounded.TButton", command=self.buscar_candidato)
        btn_buscar.pack(side="left", padx=12, pady=8)

        colunas = ("id", "municipio", "uf", "cn", "ch", "lc", "mt", "redacao")
        self.tree_candidato = ttk.Treeview(self.tab_candidato, columns=colunas, show="headings", height=5)
        self.tree_candidato.pack(fill="both", expand=True, padx=15, pady=10)

        titulos = [
            ("id", "ID", 90),
            ("municipio", "Município", 220),
            ("uf", "UF", 50),
            ("cn", "Ciências Nat.", 105),
            ("ch", "Ciências Hum.", 105),
            ("lc", "Linguagens", 105),
            ("mt", "Matemática", 105),
            ("redacao", "Redação", 105),
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
    # ABA 2: ESTATÍSTICAS POR ESTADO E MUNICÍPIO
    # -------------------------------------------------------------
    def setup_tab_estatisticas(self):
        frame_filtros = ttk.LabelFrame(self.tab_estatisticas, text=" Filtros de Agregação ")
        frame_filtros.pack(fill="x", padx=15, pady=12)

        ttk.Label(frame_filtros, text="UF (ex: GO):", background=COR_FUNDO, font=("Segoe UI", 9)).grid(row=0, column=0, padx=6, pady=8)
        self.entry_uf = ttk.Entry(frame_filtros, width=6)
        self.entry_uf.grid(row=0, column=1, padx=4, pady=8)

        ttk.Label(frame_filtros, text="Município:", background=COR_FUNDO, font=("Segoe UI", 9)).grid(row=0, column=2, padx=10, pady=8)
        self.entry_municipio = ttk.Entry(frame_filtros, width=24)
        self.entry_municipio.grid(row=0, column=3, padx=4, pady=8)

        btn_calcular = ttk.Button(frame_filtros, text="Calcular Médias", style="Rounded.TButton", command=self.calcular_estatisticas)
        btn_calcular.grid(row=0, column=4, padx=15, pady=8)

        frame_tabela = ttk.Frame(self.tab_estatisticas, style="Custom.TFrame")
        frame_tabela.pack(fill="both", expand=True, padx=15, pady=10)

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
            ("local", "Abrangência / Localidade", 260),
            ("total", "Participantes", 115),
            ("media_cn", "Média CN", 95),
            ("media_ch", "Média CH", 95),
            ("media_lc", "Média LC", 95),
            ("media_mt", "Média MT", 95),
            ("media_redacao", "Média Redação", 110),
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

        # 1. Ambos vazios: Geral do Brasil + Cada Estado
        if not uf and not municipio:
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

        # 2. Apenas UF: Total do Estado + Cidades daquele Estado
        elif uf and not municipio:
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

        # 3. Apenas Município: Cidades homônimas separadas por UF
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

        # 4. UF e Município preenchidos: Linha única exata
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
        frame_filtros_top = ttk.LabelFrame(self.tab_top10, text=" Filtros de Busca ")
        frame_filtros_top.pack(fill="x", padx=15, pady=12)

        ttk.Label(frame_filtros_top, text="Filtrar por UF (Opcional):", background=COR_FUNDO, font=("Segoe UI", 9)).pack(side="left", padx=8, pady=8)
        self.entry_top_uf = ttk.Entry(frame_filtros_top, width=6)
        self.entry_top_uf.pack(side="left", padx=4, pady=8)

        btn_top10 = ttk.Button(frame_filtros_top, text="Listar Top 10", style="Rounded.TButton", command=self.listar_top10)
        btn_top10.pack(side="left", padx=12, pady=8)

        colunas = ("posicao", "id", "municipio", "uf", "redacao", "mt")
        self.tree_top10 = ttk.Treeview(self.tab_top10, columns=colunas, show="headings", height=12)
        self.tree_top10.pack(fill="both", expand=True, padx=15, pady=10)

        titulos = [
            ("posicao", "Posição", 70),
            ("id", "ID Resultado", 115),
            ("municipio", "Município", 230),
            ("uf", "UF", 55),
            ("redacao", "Nota Redação", 110),
            ("mt", "Nota Matemática", 110),
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