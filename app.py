import sqlite3
import time
import os
import tkinter as tk
from tkinter import ttk, messagebox

import cache

# Caminho absoluto para a base de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dados", "enem_2025.db")

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"Banco de dados não encontrado em: {DB_PATH}")

COR_PRIMARIA = "#2b3980"
COR_BRANCO = "#ffffff"
COR_FUNDO = "#f4f6fa"
COR_HOVER = "#1f2a63"
COR_HIT = "#2e7d32"     # Verde para Cache HIT
COR_MISS = "#c62828"    # Vermelho para Cache MISS

def get_db_connection():
    return sqlite3.connect(DB_PATH)

class EnemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Análise ENEM 2025 - Com Camada Redis")
        largura, altura = 1020, 680
        self.centralizar_janela(largura, altura)
        self.root.minsize(840, 560)
        self.root.configure(bg=COR_FUNDO)
        self.configurar_estilos()

        # Container Principal
        container = tk.Frame(self.root, bg=COR_FUNDO)
        container.pack(fill="both", expand=True, padx=15, pady=10)

        # Cabeçalho Superior
        header = tk.Frame(container, bg=COR_PRIMARIA, height=45)
        header.pack(fill="x", pady=(0, 10))
        lbl_titulo = tk.Label(
            header,
            text="SISTEMA DE ANÁLISE ENEM 2025 (CAMADA REDIS / CACHE-ASIDE)",
            bg=COR_PRIMARIA,
            fg=COR_BRANCO,
            font=("Segoe UI", 12, "bold"),
            pady=10
        )
        lbl_titulo.pack()

        # Container de Abas
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        self.tab_candidato = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.tab_estatisticas = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.tab_top10 = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.tab_invalida = ttk.Frame(self.notebook, style="Custom.TFrame")

        self.notebook.add(self.tab_candidato, text=" Consulta por Candidato ")
        self.notebook.add(self.tab_estatisticas, text=" Estatísticas por Região ")
        self.notebook.add(self.tab_top10, text=" Top 10 Redações ")
        self.notebook.add(self.tab_invalida, text=" Corrigir Nota (Invalidação) ")

        self.setup_tab_candidato()
        self.setup_tab_estatisticas()
        self.setup_tab_top10()
        self.setup_tab_invalida()

        # Barra de Status no Rodapé (Exibe se foi HIT ou MISS e tempo de execução)
        self.frame_status = tk.Frame(container, bg="#e0e4ec", height=28)
        self.frame_status.pack(fill="x", pady=(8, 0))

        self.lbl_origem = tk.Label(
            self.frame_status,
            text="Origem: AGUARDANDO CONSULTA",
            bg="#e0e4ec",
            fg="#555555",
            font=("Segoe UI", 9, "bold"),
            padx=10
        )
        self.lbl_origem.pack(side="left")

        self.lbl_tempo = tk.Label(
            self.frame_status,
            text="Tempo: 0.00 ms",
            bg="#e0e4ec",
            fg="#555555",
            font=("Segoe UI", 9),
            padx=10
        )
        self.lbl_tempo.pack(side="left")

        btn_limpar = tk.Button(
            self.frame_status,
            text="Limpar Cache do Redis",
            bg="#d0d5dd",
            fg="#222222",
            font=("Segoe UI", 8),
            relief="flat",
            command=self.acao_limpar_cache
        )
        btn_limpar.pack(side="right", padx=5, pady=2)

    def centralizar_janela(self, largura, altura):
        self.root.update_idletasks()
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela - largura) // 2
        pos_y = (altura_tela - altura) // 2
        self.root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    def atualizar_status(self, origem, tempo_ms):
        cor = COR_HIT if "HIT" in origem else (COR_MISS if "MISS" in origem else "#555555")
        self.lbl_origem.config(text=f"Origem: {origem}", fg=cor)
        self.lbl_tempo.config(text=f"Tempo gasto: {tempo_ms:.2f} ms")

    def acao_limpar_cache(self):
        cache.limpar_todo_cache()
        messagebox.showinfo("Cache", "Todas as chaves do Redis foram apagadas.")

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Custom.TFrame", background=COR_FUNDO)
        style.configure("TLabelframe", background=COR_FUNDO, bordercolor="#d0d5dd")
        style.configure("TLabelframe.Label", background=COR_FUNDO, foreground=COR_PRIMARIA, font=("Segoe UI", 9, "bold"))

        style.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background="#dbe1f1",
            foreground=COR_PRIMARIA,
            font=("Segoe UI", 9, "bold"),
            padding=[12, 6]
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COR_PRIMARIA)],
            foreground=[("selected", COR_BRANCO)]
        )

        style.configure(
            "Rounded.TButton",
            background=COR_PRIMARIA,
            foreground=COR_BRANCO,
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            padding=[12, 6]
        )
        style.map(
            "Rounded.TButton",
            background=[("active", COR_HOVER), ("pressed", "#151c42")],
            foreground=[("active", COR_BRANCO)]
        )

        style.configure("TEntry", fieldbackground=COR_BRANCO, foreground="#222222", padding=4)

        style.configure(
            "Treeview",
            background=COR_BRANCO,
            foreground="#222222",
            fieldbackground=COR_BRANCO,
            rowheight=24,
            font=("Segoe UI", 9),
            borderwidth=0
        )
        style.map("Treeview", background=[("selected", COR_PRIMARIA)], foreground=[("selected", COR_BRANCO)])
        style.configure(
            "Treeview.Heading",
            background=COR_PRIMARIA,
            foreground=COR_BRANCO,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=[4, 6]
        )
        style.map("Treeview.Heading", background=[("active", COR_HOVER)], foreground=[("active", COR_BRANCO)])

    # -------------------------------------------------------------
    # ABA 1: CONSULTA POR CANDIDATO (Leitura direta por PK no SQLite)
    # -------------------------------------------------------------
    def setup_tab_candidato(self):
        frame_busca = ttk.LabelFrame(self.tab_candidato, text=" Buscar Candidato ")
        frame_busca.pack(fill="x", padx=15, pady=10)

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

        t_inicio = time.perf_counter()
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
        t_total = (time.perf_counter() - t_inicio) * 1000

        self.atualizar_status("SQLITE (BUSCA DIRETA POR PK)", t_total)

        if resultado:
            dados_formatados = [val if val is not None else "-" for val in resultado]
            self.tree_candidato.insert("", "end", values=dados_formatados)
        else:
            messagebox.showinfo("Busca", "Nenhum candidato encontrado com este ID.")

    # -------------------------------------------------------------
    # ABA 2: ESTATÍSTICAS POR REGIÃO (Com Cache-Aside do Redis)
    # -------------------------------------------------------------
    def setup_tab_estatisticas(self):
        frame_filtros = ttk.LabelFrame(self.tab_estatisticas, text=" Filtros de Agregação ")
        frame_filtros.pack(fill="x", padx=15, pady=10)

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

        mun_norm = cache.normalizar_texto(municipio)
        if not uf and not municipio:
            chave_cache = "enem:stats:brasil_completo"
        elif uf and not municipio:
            chave_cache = f"enem:stats:uf:{uf}"
        elif not uf and municipio:
            chave_cache = f"enem:stats:mun:{mun_norm}"
        else:
            chave_cache = f"enem:stats:uf:{uf}:mun:{mun_norm}"

        def busca_no_sqlite():
            conn = get_db_connection()
            cursor = conn.cursor()
            linhas = []

            # 1. Ambos vazios: Brasil + Cada Estado
            if not uf and not municipio:
                cursor.execute("""
                    SELECT COUNT(*), ROUND(AVG(NU_NOTA_CN), 2), ROUND(AVG(NU_NOTA_CH), 2),
                           ROUND(AVG(NU_NOTA_LC), 2), ROUND(AVG(NU_NOTA_MT), 2), ROUND(AVG(NU_NOTA_REDACAO), 2)
                    FROM resultados_enem
                """)
                brasil = cursor.fetchone()
                if brasil and brasil[0] > 0:
                    linhas.append(["BRASIL (CONSOLIDADO)", f"{brasil[0]:,}"] + [v if v is not None else "-" for v in brasil[1:]])

                cursor.execute("""
                    SELECT SG_UF_PROVA, COUNT(*), ROUND(AVG(NU_NOTA_CN), 2), ROUND(AVG(NU_NOTA_CH), 2),
                           ROUND(AVG(NU_NOTA_LC), 2), ROUND(AVG(NU_NOTA_MT), 2), ROUND(AVG(NU_NOTA_REDACAO), 2)
                    FROM resultados_enem WHERE SG_UF_PROVA IS NOT NULL
                    GROUP BY SG_UF_PROVA ORDER BY SG_UF_PROVA ASC
                """)
                for est in cursor.fetchall():
                    linhas.append([f"Estado: {est[0]}", f"{est[1]:,}"] + [v if v is not None else "-" for v in est[2:]])

            # 2. Apenas UF: Estado + Cidades
            elif uf and not municipio:
                cursor.execute("""
                    SELECT COUNT(*), ROUND(AVG(NU_NOTA_CN), 2), ROUND(AVG(NU_NOTA_CH), 2),
                           ROUND(AVG(NU_NOTA_LC), 2), ROUND(AVG(NU_NOTA_MT), 2), ROUND(AVG(NU_NOTA_REDACAO), 2)
                    FROM resultados_enem WHERE SG_UF_PROVA = ?
                """, (uf,))
                est_cons = cursor.fetchone()
                if est_cons and est_cons[0] > 0:
                    linhas.append([f"ESTADO {uf} (CONSOLIDADO)", f"{est_cons[0]:,}"] + [v if v is not None else "-" for v in est_cons[1:]])

                cursor.execute("""
                    SELECT NO_MUNICIPIO_PROVA, COUNT(*), ROUND(AVG(NU_NOTA_CN), 2), ROUND(AVG(NU_NOTA_CH), 2),
                           ROUND(AVG(NU_NOTA_LC), 2), ROUND(AVG(NU_NOTA_MT), 2), ROUND(AVG(NU_NOTA_REDACAO), 2)
                    FROM resultados_enem WHERE SG_UF_PROVA = ? AND NO_MUNICIPIO_PROVA IS NOT NULL
                    GROUP BY NO_MUNICIPIO_PROVA ORDER BY NO_MUNICIPIO_PROVA ASC
                """, (uf,))
                for cid in cursor.fetchall():
                    linhas.append([f"{cid[0]} ({uf})", f"{cid[1]:,}"] + [v if v is not None else "-" for v in cid[2:]])

            # 3. Apenas Município
            elif not uf and municipio:
                cursor.execute("""
                    SELECT NO_MUNICIPIO_PROVA, SG_UF_PROVA, COUNT(*), ROUND(AVG(NU_NOTA_CN), 2), ROUND(AVG(NU_NOTA_CH), 2),
                           ROUND(AVG(NU_NOTA_LC), 2), ROUND(AVG(NU_NOTA_MT), 2), ROUND(AVG(NU_NOTA_REDACAO), 2)
                    FROM resultados_enem WHERE UPPER(NO_MUNICIPIO_PROVA) = UPPER(?)
                    GROUP BY NO_MUNICIPIO_PROVA, SG_UF_PROVA ORDER BY SG_UF_PROVA ASC
                """, (municipio,))
                for cid in cursor.fetchall():
                    linhas.append([f"{cid[0]} - {cid[1]}", f"{cid[2]:,}"] + [v if v is not None else "-" for v in cid[3:]])

            # 4. UF e Município preenchidos
            else:
                cursor.execute("""
                    SELECT COUNT(*), ROUND(AVG(NU_NOTA_CN), 2), ROUND(AVG(NU_NOTA_CH), 2),
                           ROUND(AVG(NU_NOTA_LC), 2), ROUND(AVG(NU_NOTA_MT), 2), ROUND(AVG(NU_NOTA_REDACAO), 2)
                    FROM resultados_enem WHERE SG_UF_PROVA = ? AND UPPER(NO_MUNICIPIO_PROVA) = UPPER(?)
                """, (uf, municipio))
                res = cursor.fetchone()
                if res and res[0] > 0:
                    linhas.append([f"{municipio} - {uf}", f"{res[0]:,}"] + [v if v is not None else "-" for v in res[1:]])

            conn.close()
            return linhas

        t_inicio = time.perf_counter()
        dados, origem = cache.buscar_com_cache(chave_cache, busca_no_sqlite, ttl_segundos=86400)
        t_total = (time.perf_counter() - t_inicio) * 1000

        self.atualizar_status(f"{origem} | Chave: {chave_cache}", t_total)

        if dados:
            for linha in dados:
                self.tree_stats.insert("", "end", values=linha)
        else:
            messagebox.showinfo("Estatísticas", "Nenhum dado encontrado para os filtros informados.")

    # -------------------------------------------------------------
    # ABA 3: TOP 10 REDAÇÕES (Com Cache-Aside do Redis)
    # -------------------------------------------------------------
    def setup_tab_top10(self):
        frame_filtros_top = ttk.LabelFrame(self.tab_top10, text=" Filtros de Busca ")
        frame_filtros_top.pack(fill="x", padx=15, pady=10)

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

        chave_cache = f"enem:top10:uf:{uf}" if uf else "enem:top10:todas"

        def busca_top10_sqlite():
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
            linhas = cursor.fetchall()
            conn.close()

            return [
                [f"{idx}º", res[0], res[1], res[2], res[3], res[4] if res[4] is not None else "-"]
                for idx, res in enumerate(linhas, 1)
            ]

        t_inicio = time.perf_counter()
        dados, origem = cache.buscar_com_cache(chave_cache, busca_top10_sqlite, ttl_segundos=86400)
        t_total = (time.perf_counter() - t_inicio) * 1000

        self.atualizar_status(f"{origem} | Chave: {chave_cache}", t_total)

        if dados:
            for linha in dados:
                self.tree_top10.insert("", "end", values=linha)
        else:
            messagebox.showinfo("Top 10", "Nenhum resultado localizado.")

    # -------------------------------------------------------------
    # ABA 4: CORRIGIR NOTA (Escrita no SQLite + Invalidação no Redis)
    # -------------------------------------------------------------
    def setup_tab_invalida(self):
        frame_form = ttk.LabelFrame(self.tab_invalida, text=" Simular Recurso e Atualizar Nota (Invalidação no Redis) ")
        frame_form.pack(fill="x", padx=15, pady=15)

        ttk.Label(frame_form, text="ID Resultado:", background=COR_FUNDO).grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.entry_inv_id = ttk.Entry(frame_form, width=15)
        self.entry_inv_id.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(frame_form, text="Nova Nota Redação (0 a 1000):", background=COR_FUNDO).grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.entry_inv_nota = ttk.Entry(frame_form, width=15)
        self.entry_inv_nota.grid(row=1, column=1, padx=8, pady=8)

        btn_atualizar = ttk.Button(frame_form, text="Gravar no SQLite e Invalidar Cache", style="Rounded.TButton", command=self.executar_invalidação)
        btn_atualizar.grid(row=2, column=0, columnspan=2, padx=8, pady=15)

        lbl_explicativo = tk.Label(
            self.tab_invalida,
            text=(
                "COMO FUNCIONA ESTE FLUXO (Semana 3):\n\n"
                "1. A aplicação executa UPDATE e COMMIT no banco relacional (fonte da verdade primeiro).\n"
                "2. Em seguida, descobre a UF e Município do aluno e dispara DEL no Redis para as chaves afetadas.\n"
                "3. Ao voltar na aba 'Estatísticas' e buscar novamente, o sistema dará Cache MISS,\n"
                "   recalculando os valores atualizados do SQLite e gravando a nova média no Redis."
            ),
            bg=COR_FUNDO,
            fg="#444444",
            font=("Segoe UI", 9),
            justify="left"
        )
        lbl_explicativo.pack(padx=20, pady=10, anchor="w")

    def executar_invalidação(self):
        id_str = self.entry_inv_id.get().strip()
        nota_str = self.entry_inv_nota.get().strip().replace(",", ".")

        if not id_str.isdigit():
            messagebox.showwarning("Aviso", "Informe um ID numérico válido.")
            return

        try:
            nova_nota = float(nota_str)
            if nova_nota < 0 or nova_nota > 1000:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Aviso", "A nota deve ser um número entre 0 e 1000.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT SG_UF_PROVA, NO_MUNICIPIO_PROVA FROM resultados_enem WHERE ID_RESULTADO = ?", (int(id_str),))
        cand = cursor.fetchone()

        if not cand:
            conn.close()
            messagebox.showerror("Erro", "Candidato não encontrado no banco de dados.")
            return

        uf_cand, mun_cand = cand[0], cand[1]

        # 1. Fonte da verdade PRIMEIRO (SQLite UPDATE + COMMIT)
        t_inicio = time.perf_counter()
        cursor.execute("UPDATE resultados_enem SET NU_NOTA_REDACAO = ? WHERE ID_RESULTADO = ?", (nova_nota, int(id_str)))
        conn.commit()
        conn.close()

        # 2. Invalidação no Redis (DEL das chaves afetadas)
        mun_norm = cache.normalizar_texto(mun_cand)
        chaves_afetadas = [
            "enem:stats:brasil_completo",
            f"enem:stats:uf:{uf_cand}",
            f"enem:stats:mun:{mun_norm}",
            f"enem:stats:uf:{uf_cand}:mun:{mun_norm}",
            "enem:top10:todas",
            f"enem:top10:uf:{uf_cand}"
        ]
        cache.invalidar_chaves(chaves_afetadas)
        t_total = (time.perf_counter() - t_inicio) * 1000

        self.atualizar_status("ESCRITA SQLITE + DEL REDIS", t_total)
        messagebox.showinfo(
            "Sucesso",
            f"Nota do candidato {id_str} atualizada para {nova_nota}!\n\n"
            f"Chaves invalidadas no Redis:\n" + "\n".join(chaves_afetadas)
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = EnemApp(root)
    root.mainloop()