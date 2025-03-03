import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import os

class FluxoDeCaixaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Fluxo de Caixa")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)
        
        # Configurar banco de dados
        self.setup_database()
        
        # Variáveis
        self.transacao_selecionada = None
        
        # Criar interface
        self.criar_interface()
        
        # Carregar dados iniciais
        self.carregar_transacoes()
        self.atualizar_saldo()
        
    def setup_database(self):
        # Verificar se o diretório 'data' existe, se não, criar
        if not os.path.exists("data"):
            os.makedirs("data")
            
        self.conn = sqlite3.connect("data/fluxo_caixa.db")
        self.cursor = self.conn.cursor()
        
        # Criar tabela de categorias se não existir
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL
        )
        ''')
        
        # Criar tabela de transações se não existir
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY,
            data TEXT NOT NULL,
            descricao TEXT NOT NULL,
            categoria_id INTEGER,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
        ''')
        
        # Inserir categorias padrão se não existirem
        categorias_padrao = [
            ("Vendas", "entrada"),
            ("Serviços", "entrada"),
            ("Investimentos", "entrada"),
            ("Outras Receitas", "entrada"),
            ("Materiais", "saida"),
            ("Salários", "saida"),
            ("Aluguel", "saida"),
            ("Impostos", "saida"),
            ("Fornecedores", "saida"),
            ("Despesas Operacionais", "saida"),
            ("Outras Despesas", "saida")
        ]
        
        for categoria in categorias_padrao:
            try:
                self.cursor.execute("INSERT INTO categorias (nome, tipo) VALUES (?, ?)", categoria)
            except sqlite3.IntegrityError:
                pass  # Categoria já existe
                
        self.conn.commit()
    
    def criar_interface(self):
        # Frame principal dividido em duas partes
        self.frame_principal = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame esquerdo - Lista de transações e controles
        self.frame_esquerdo = ttk.Frame(self.frame_principal)
        self.frame_principal.add(self.frame_esquerdo, weight=2)
        
        # Frame direito - Gráficos e estatísticas
        self.frame_direito = ttk.Frame(self.frame_principal)
        self.frame_principal.add(self.frame_direito, weight=1)
        
        # === FRAME ESQUERDO ===
        # Frame para saldo
        self.frame_saldo = ttk.LabelFrame(self.frame_esquerdo, text="Resumo")
        self.frame_saldo.pack(fill=tk.X, padx=5, pady=5)
        
        # Labels para saldo
        self.label_saldo = ttk.Label(self.frame_saldo, text="Saldo Atual: R$ 0,00", font=("Arial", 14, "bold"))
        self.label_saldo.grid(row=0, column=0, padx=10, pady=5)
        
        self.label_entradas = ttk.Label(self.frame_saldo, text="Total Entradas: R$ 0,00", font=("Arial", 12))
        self.label_entradas.grid(row=1, column=0, padx=10, pady=2, sticky="w")
        
        self.label_saidas = ttk.Label(self.frame_saldo, text="Total Saídas: R$ 0,00", font=("Arial", 12))
        self.label_saidas.grid(row=2, column=0, padx=10, pady=2, sticky="w")
        
        # Frame para botões
        self.frame_botoes = ttk.Frame(self.frame_esquerdo)
        self.frame_botoes.pack(fill=tk.X, padx=5, pady=5)
        
        # Botões para adicionar transações
        self.btn_adicionar_entrada = ttk.Button(self.frame_botoes, text="+ Entrada", command=lambda: self.abrir_form_transacao("entrada"))
        self.btn_adicionar_entrada.grid(row=0, column=0, padx=5, pady=5)
        
        self.btn_adicionar_saida = ttk.Button(self.frame_botoes, text="+ Saída", command=lambda: self.abrir_form_transacao("saida"))
        self.btn_adicionar_saida.grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_editar = ttk.Button(self.frame_botoes, text="Editar", command=self.editar_transacao, state=tk.DISABLED)
        self.btn_editar.grid(row=0, column=2, padx=5, pady=5)
        
        self.btn_excluir = ttk.Button(self.frame_botoes, text="Excluir", command=self.excluir_transacao, state=tk.DISABLED)
        self.btn_excluir.grid(row=0, column=3, padx=5, pady=5)
        
        self.btn_categorias = ttk.Button(self.frame_botoes, text="Gerenciar Categorias", command=self.abrir_gerenciador_categorias)
        self.btn_categorias.grid(row=0, column=4, padx=5, pady=5)
        
        # Frame para filtros
        self.frame_filtros = ttk.LabelFrame(self.frame_esquerdo, text="Filtros")
        self.frame_filtros.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.frame_filtros, text="Mês:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_mes = ttk.Combobox(self.frame_filtros, values=["Todos", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
        self.combo_mes.current(0)
        self.combo_mes.grid(row=0, column=1, padx=5, pady=5)
        self.combo_mes.bind("<<ComboboxSelected>>", self.aplicar_filtros)
        
        ttk.Label(self.frame_filtros, text="Ano:").grid(row=0, column=2, padx=5, pady=5)
        anos = ["Todos"] + [str(ano) for ano in range(datetime.now().year - 5, datetime.now().year + 1)]
        self.combo_ano = ttk.Combobox(self.frame_filtros, values=anos)
        self.combo_ano.current(anos.index(str(datetime.now().year)))
        self.combo_ano.grid(row=0, column=3, padx=5, pady=5)
        self.combo_ano.bind("<<ComboboxSelected>>", self.aplicar_filtros)
        
        ttk.Label(self.frame_filtros, text="Tipo:").grid(row=0, column=4, padx=5, pady=5)
        self.combo_tipo = ttk.Combobox(self.frame_filtros, values=["Todos", "Entradas", "Saídas"])
        self.combo_tipo.current(0)
        self.combo_tipo.grid(row=0, column=5, padx=5, pady=5)
        self.combo_tipo.bind("<<ComboboxSelected>>", self.aplicar_filtros)
        
        # Frame para tabela de transações
        self.frame_transacoes = ttk.LabelFrame(self.frame_esquerdo, text="Transações")
        self.frame_transacoes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tabela de transações
        colunas = ("Data", "Descrição", "Categoria", "Valor", "Tipo")
        self.tabela_transacoes = ttk.Treeview(self.frame_transacoes, columns=colunas, show="headings")
        
        # Configurar cabeçalhos
        for col in colunas:
            self.tabela_transacoes.heading(col, text=col)
            
        # Configurar larguras das colunas
        self.tabela_transacoes.column("Data", width=100)
        self.tabela_transacoes.column("Descrição", width=200)
        self.tabela_transacoes.column("Categoria", width=150)
        self.tabela_transacoes.column("Valor", width=100)
        self.tabela_transacoes.column("Tipo", width=100)
        
        # Scrollbar para a tabela
        scrollbar = ttk.Scrollbar(self.frame_transacoes, orient=tk.VERTICAL, command=self.tabela_transacoes.yview)
        self.tabela_transacoes.configure(yscroll=scrollbar.set)
        
        # Evento de seleção
        self.tabela_transacoes.bind("<<TreeviewSelect>>", self.ao_selecionar_transacao)
        
        # Empacotar tabela e scrollbar
        self.tabela_transacoes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === FRAME DIREITO ===
        # Frame para gráfico de fluxo mensal
        self.frame_grafico_mensal = ttk.LabelFrame(self.frame_direito, text="Fluxo de Caixa Mensal")
        self.frame_grafico_mensal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Figura para o gráfico
        self.fig_mensal = plt.Figure(figsize=(5, 4), dpi=100)
        self.canvas_mensal = FigureCanvasTkAgg(self.fig_mensal, self.frame_grafico_mensal)
        self.canvas_mensal.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Frame para gráfico de distribuição
        self.frame_grafico_distribuicao = ttk.LabelFrame(self.frame_direito, text="Distribuição de Despesas")
        self.frame_grafico_distribuicao.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Figura para o gráfico de pizza
        self.fig_distribuicao = plt.Figure(figsize=(5, 4), dpi=100)
        self.canvas_distribuicao = FigureCanvasTkAgg(self.fig_distribuicao, self.frame_grafico_distribuicao)
        self.canvas_distribuicao.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def carregar_transacoes(self):
        # Limpar tabela
        for item in self.tabela_transacoes.get_children():
            self.tabela_transacoes.delete(item)
            
        # Construir query baseada nos filtros
        query = """
        SELECT t.id, t.data, t.descricao, c.nome, t.valor, t.tipo 
        FROM transacoes t
        LEFT JOIN categorias c ON t.categoria_id = c.id
        WHERE 1=1
        """
        params = []
        
        # Aplicar filtro de mês
        mes_selecionado = self.combo_mes.get()
        if mes_selecionado != "Todos":
            meses = {"Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04", "Maio": "05", "Junho": "06",
                     "Julho": "07", "Agosto": "08", "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"}
            mes_num = meses[mes_selecionado]
            query += " AND strftime('%m', t.data) = ?"
            params.append(mes_num)
            
        # Aplicar filtro de ano
        ano_selecionado = self.combo_ano.get()
        if ano_selecionado != "Todos":
            query += " AND strftime('%Y', t.data) = ?"
            params.append(ano_selecionado)
            
        # Aplicar filtro de tipo
        tipo_selecionado = self.combo_tipo.get()
        if tipo_selecionado == "Entradas":
            query += " AND t.tipo = 'entrada'"
        elif tipo_selecionado == "Saídas":
            query += " AND t.tipo = 'saida'"
            
        # Ordenar por data
        query += " ORDER BY t.data DESC"
        
        # Executar query
        self.cursor.execute(query, params)
        
        # Preencher tabela
        for row in self.cursor.fetchall():
            id_transacao, data, descricao, categoria, valor, tipo = row
            
            # Formatar data
            data_formatada = data
            try:
                data_obj = datetime.strptime(data, "%Y-%m-%d")
                data_formatada = data_obj.strftime("%d/%m/%Y")
            except ValueError:
                pass
                
            # Formatar valor
            valor_formatado = f"R$ {valor:.2f}"
            
            # Formatar tipo
            tipo_formatado = "Entrada" if tipo == "entrada" else "Saída"
            
            # Inserir na tabela
            self.tabela_transacoes.insert("", tk.END, iid=id_transacao, values=(
                data_formatada, descricao, categoria, valor_formatado, tipo_formatado
            ))
            
        # Atualizar gráficos
        self.atualizar_graficos()
    
    def abrir_form_transacao(self, tipo):
        # Criar janela de formulário
        form = tk.Toplevel(self.root)
        form.title("Adicionar " + ("Entrada" if tipo == "entrada" else "Saída"))
        form.geometry("400x300")
        form.resizable(False, False)
        form.transient(self.root)
        form.grab_set()
        
        # Variáveis do formulário
        self.var_data = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.var_descricao = tk.StringVar()
        self.var_categoria = tk.StringVar()
        self.var_valor = tk.DoubleVar()
        
        # Frame para formulário
        frame_form = ttk.Frame(form, padding=10)
        frame_form.pack(fill=tk.BOTH, expand=True)
        
        # Campos do formulário
        ttk.Label(frame_form, text="Data:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        entry_data = ttk.Entry(frame_form, textvariable=self.var_data)
        entry_data.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Descrição:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        entry_descricao = ttk.Entry(frame_form, textvariable=self.var_descricao)
        entry_descricao.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Categoria:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Buscar categorias do banco de dados
        self.cursor.execute("SELECT id, nome FROM categorias WHERE tipo = ?", (tipo,))
        categorias = self.cursor.fetchall()
        categorias_nomes = [cat[1] for cat in categorias]
        
        combo_categoria = ttk.Combobox(frame_form, textvariable=self.var_categoria, values=categorias_nomes)
        if categorias_nomes:
            combo_categoria.current(0)
        combo_categoria.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Valor (R$):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        entry_valor = ttk.Entry(frame_form, textvariable=self.var_valor)
        entry_valor.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Botões
        frame_botoes = ttk.Frame(frame_form)
        frame_botoes.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_botoes, text="Salvar", command=lambda: self.salvar_transacao(form, tipo, None)).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Cancelar", command=form.destroy).pack(side=tk.LEFT, padx=5)
    
    def editar_transacao(self):
        if not self.transacao_selecionada:
            return
            
        # Obter dados da transação selecionada
        self.cursor.execute("""
        SELECT t.data, t.descricao, c.nome, t.valor, t.tipo, t.categoria_id
        FROM transacoes t
        LEFT JOIN categorias c ON t.categoria_id = c.id
        WHERE t.id = ?
        """, (self.transacao_selecionada,))
        
        transacao = self.cursor.fetchone()
        if not transacao:
            return
            
        data, descricao, categoria, valor, tipo, categoria_id = transacao
        
        # Criar janela de formulário
        form = tk.Toplevel(self.root)
        form.title("Editar Transação")
        form.geometry("400x300")
        form.resizable(False, False)
        form.transient(self.root)
        form.grab_set()
        
        # Variáveis do formulário
        self.var_data = tk.StringVar(value=data)
        self.var_descricao = tk.StringVar(value=descricao)
        self.var_categoria = tk.StringVar(value=categoria if categoria else "")
        self.var_valor = tk.DoubleVar(value=valor)
        
        # Frame para formulário
        frame_form = ttk.Frame(form, padding=10)
        frame_form.pack(fill=tk.BOTH, expand=True)
        
        # Campos do formulário
        ttk.Label(frame_form, text="Data:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        entry_data = ttk.Entry(frame_form, textvariable=self.var_data)
        entry_data.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Descrição:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        entry_descricao = ttk.Entry(frame_form, textvariable=self.var_descricao)
        entry_descricao.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Categoria:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Buscar categorias do banco de dados
        self.cursor.execute("SELECT id, nome FROM categorias WHERE tipo = ?", (tipo,))
        categorias = self.cursor.fetchall()
        categorias_nomes = [cat[1] for cat in categorias]
        
        combo_categoria = ttk.Combobox(frame_form, textvariable=self.var_categoria, values=categorias_nomes)
        combo_categoria.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Valor (R$):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        entry_valor = ttk.Entry(frame_form, textvariable=self.var_valor)
        entry_valor.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Botões
        frame_botoes = ttk.Frame(frame_form)
        frame_botoes.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_botoes, text="Salvar", command=lambda: self.salvar_transacao(form, tipo, self.transacao_selecionada)).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Cancelar", command=form.destroy).pack(side=tk.LEFT, padx=5)
    
    def salvar_transacao(self, form, tipo, id_transacao=None):
        try:
            # Validar dados
            data = self.var_data.get()
            descricao = self.var_descricao.get()
            categoria_nome = self.var_categoria.get()
            valor = self.var_valor.get()
            
            if not data or not descricao or not categoria_nome or valor <= 0:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios e o valor deve ser maior que zero.")
                return
                
            # Validar formato da data
            try:
                datetime.strptime(data, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use AAAA-MM-DD.")
                return
                
            # Obter ID da categoria
            self.cursor.execute("SELECT id FROM categorias WHERE nome = ?", (categoria_nome,))
            resultado = self.cursor.fetchone()
            
            if not resultado:
                messagebox.showerror("Erro", "Categoria não encontrada.")
                return
                
            categoria_id = resultado[0]
            
            # Inserir ou atualizar no banco de dados
            if id_transacao:  # Editar
                self.cursor.execute("""
                UPDATE transacoes 
                SET data = ?, descricao = ?, categoria_id = ?, valor = ?
                WHERE id = ?
                """, (data, descricao, categoria_id, valor, id_transacao))
            else:  # Novo
                self.cursor.execute("""
                INSERT INTO transacoes (data, descricao, categoria_id, valor, tipo)
                VALUES (?, ?, ?, ?, ?)
                """, (data, descricao, categoria_id, valor, tipo))
                
            self.conn.commit()
            
            # Fechar formulário
            form.destroy()
            
            # Recarregar dados
            self.carregar_transacoes()
            self.atualizar_saldo()
            
            # Mensagem de sucesso
            operacao = "atualizada" if id_transacao else "adicionada"
            messagebox.showinfo("Sucesso", f"Transação {operacao} com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    
    def excluir_transacao(self):
        if not self.transacao_selecionada:
            return
            
        # Confirmar exclusão
        confirmacao = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta transação?")
        if not confirmacao:
            return
            
        try:
            # Excluir do banco de dados
            self.cursor.execute("DELETE FROM transacoes WHERE id = ?", (self.transacao_selecionada,))
            self.conn.commit()
            
            # Recarregar dados
            self.carregar_transacoes()
            self.atualizar_saldo()
            
            # Desabilitar botões
            self.btn_editar.configure(state=tk.DISABLED)
            self.btn_excluir.configure(state=tk.DISABLED)
            
            # Mensagem de sucesso
            messagebox.showinfo("Sucesso", "Transação excluída com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    
    def ao_selecionar_transacao(self, event):
        # Obter ID da transação selecionada
        selecionados = self.tabela_transacoes.selection()
        if selecionados:
            self.transacao_selecionada = selecionados[0]
            self.btn_editar.configure(state=tk.NORMAL)
            self.btn_excluir.configure(state=tk.NORMAL)
        else:
            self.transacao_selecionada = None
            self.btn_editar.configure(state=tk.DISABLED)
            self.btn_excluir.configure(state=tk.DISABLED)
    
    def aplicar_filtros(self, event=None):
        self.carregar_transacoes()
        self.atualizar_saldo()
    
    def atualizar_saldo(self):
        # Construir query baseada nos filtros
        query = "SELECT tipo, SUM(valor) FROM transacoes WHERE 1=1"
        params = []
        
        # Aplicar filtro de mês
        mes_selecionado = self.combo_mes.get()
        if mes_selecionado != "Todos":
            meses = {"Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04", "Maio": "05", "Junho": "06",
                     "Julho": "07", "Agosto": "08", "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"}
            mes_num = meses[mes_selecionado]
            query += " AND strftime('%m', data) = ?"
            params.append(mes_num)
            
        # Aplicar filtro de ano
        ano_selecionado = self.combo_ano.get()
        if ano_selecionado != "Todos":
            query += " AND strftime('%Y', data) = ?"
            params.append(ano_selecionado)
            
        # Agrupar por tipo
        query += " GROUP BY tipo"
        
        # Executar query
        self.cursor.execute(query, params)
        
        # Calcular saldo
        entradas = 0
        saidas = 0
        
        for row in self.cursor.fetchall():
            tipo, total = row
            if tipo == "entrada":
                entradas = total
            elif tipo == "saida":
                saidas = total
                
        saldo = entradas - saidas
        
        # Atualizar labels
        self.label_saldo.configure(text=f"Saldo Atual: R$ {saldo:.2f}")
        self.label_entradas.configure(text=f"Total Entradas: R$ {entradas:.2f}")
        self.label_saidas.configure(text=f"Total Saídas: R$ {saidas:.2f}")
        
        # Mudar cor do saldo conforme valor
        if saldo > 0:
            self.label_saldo.configure(foreground="dark green")
        elif saldo < 0:
            self.label_saldo.configure(foreground="red")
        else:
            self.label_saldo.configure(foreground="black")
    
    def atualizar_graficos(self):
        self.atualizar_grafico_mensal()
        self.atualizar_grafico_distribuicao()
    
    def atualizar_grafico_mensal(self):
        # Limpar gráfico anterior
        self.fig_mensal.clear()
        
        # Obter dados para o gráfico
        query = """
        SELECT strftime('%Y-%m', data) as mes, tipo, SUM(valor) as total
        FROM transacoes
        """
        
        params = []
        where_clauses = []
        
        # Aplicar filtro de ano
        ano_selecionado = self.combo_ano.get()
        if ano_selecionado != "Todos":
            where_clauses.append("strftime('%Y', data) = ?")
            params.append(ano_selecionado)
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " GROUP BY mes, tipo ORDER BY mes"
        
        self.cursor.execute(query, params)
        dados = self.cursor.fetchall()
        
        # Processar dados
        meses = []
        entradas = []
        saidas = []
        saldos = []
        
        dados_dict = {}
        for mes, tipo, valor in dados:
            if mes not in dados_dict:
                dados_dict[mes] = {"entrada": 0, "saida": 0}
            dados_dict[mes][tipo] = valor
            
        for mes in sorted(dados_dict.keys()):
            # Formatar nome do mês
            mes_data = datetime.strptime(mes, "%Y-%m")
            # Formatar nome do mês
            mes_data = datetime.strptime(mes, "%Y-%m")
            mes_formatado = mes_data.strftime("%b/%y")
            
            meses.append(mes_formatado)
            entrada = dados_dict[mes].get("entrada", 0)
            saida = dados_dict[mes].get("saida", 0)
            saldo = entrada - saida
            
            entradas.append(entrada)
            saidas.append(saida)
            saldos.append(saldo)
            
        # Criar gráfico
        ax = self.fig_mensal.add_subplot(111)
        
        # Definir largura das barras
        bar_width = 0.25
        indice = range(len(meses))
        
        # Criar barras
        bar1 = ax.bar([i - bar_width for i in indice], entradas, bar_width, label='Entradas', color='green', alpha=0.7)
        bar2 = ax.bar(indice, saidas, bar_width, label='Saídas', color='red', alpha=0.7)
        bar3 = ax.bar([i + bar_width for i in indice], saldos, bar_width, label='Saldo', color='blue', alpha=0.7)
        
        # Adicionar valores nas barras
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                valor = height if height >= 0 else -height
                ax.text(bar.get_x() + bar.get_width()/2., 
                        height if height >= 0 else 0,
                        f'R${valor:.0f}',
                        ha='center', va='bottom' if height >= 0 else 'top',
                        rotation=90, fontsize=8)
                        
        add_labels(bar1)
        add_labels(bar2)
        add_labels(bar3)
        
        # Configurar gráfico
        ax.set_xlabel('Mês')
        ax.set_ylabel('Valor (R$)')
        ax.set_title('Fluxo Mensal')
        ax.set_xticks(indice)
        ax.set_xticklabels(meses, rotation=45)
        ax.legend()
        
        # Ajustar layout
        self.fig_mensal.tight_layout()
        
        # Atualizar canvas
        self.canvas_mensal.draw()
    
    def atualizar_grafico_distribuicao(self):
        # Limpar gráfico anterior
        self.fig_distribuicao.clear()
        
        # Iniciar a query sem o WHERE fixo
        query = """
        SELECT c.nome, SUM(t.valor) as total
        FROM transacoes t
        JOIN categorias c ON t.categoria_id = c.id
        """
        
        params = []
        # Adicionar condição inicial à lista de cláusulas
        where_clauses = ["t.tipo = 'saida'"]
        
        # Aplicar filtro de mês
        mes_selecionado = self.combo_mes.get()
        if mes_selecionado != "Todos":
            meses = {"Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04", "Maio": "05", "Junho": "06",
                    "Julho": "07", "Agosto": "08", "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"}
            mes_num = meses[mes_selecionado]
            where_clauses.append("strftime('%m', t.data) = ?")
            params.append(mes_num)
        
        # Aplicar filtro de ano
        ano_selecionado = self.combo_ano.get()
        if ano_selecionado != "Todos":
            where_clauses.append("strftime('%Y', t.data) = ?")
            params.append(ano_selecionado)
        
        # Adicionar as cláusulas WHERE dinamicamente
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " GROUP BY c.nome ORDER BY total DESC"
        
        self.cursor.execute(query, params)
        dados = self.cursor.fetchall()
        
        # Se não houver dados, mostrar mensagem
        if not dados:
            ax = self.fig_distribuicao.add_subplot(111)
            ax.text(0.5, 0.5, "Sem dados para o período selecionado", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes)
            self.canvas_distribuicao.draw()
            return
            
        # Processar dados
        categorias = []
        valores = []
        
        for categoria, valor in dados:
            categorias.append(categoria)
            valores.append(valor)
            
        # Criar gráfico de pizza
        ax = self.fig_distribuicao.add_subplot(111)
        wedges, texts, autotexts = ax.pie(valores, labels=None, autopct='%1.1f%%',
                                        startangle=90, shadow=False)
        
        # Adicionar legenda
        ax.legend(wedges, categorias, title="Categorias", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        # Configurar gráfico
        ax.set_title('Distribuição de Despesas')
        
        # Ajustar layout
        self.fig_distribuicao.tight_layout()
        
        # Atualizar canvas
        self.canvas_distribuicao.draw()

    
    def abrir_gerenciador_categorias(self):
        # Criar janela
        janela = tk.Toplevel(self.root)
        janela.title("Gerenciador de Categorias")
        janela.geometry("600x400")
        janela.transient(self.root)
        janela.grab_set()
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame para entradas
        frame_entradas = ttk.LabelFrame(frame_principal, text="Categorias de Entrada")
        frame_entradas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)
        
        # Frame para saídas
        frame_saidas = ttk.LabelFrame(frame_principal, text="Categorias de Saída")
        frame_saidas.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=5, pady=5)
        
        # Listas de categorias
        lista_entradas = tk.Listbox(frame_entradas)
        lista_entradas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        lista_saidas = tk.Listbox(frame_saidas)
        lista_saidas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Carregar categorias
        def carregar_categorias():
            lista_entradas.delete(0, tk.END)
            lista_saidas.delete(0, tk.END)
            
            self.cursor.execute("SELECT id, nome, tipo FROM categorias ORDER BY nome")
            for cat in self.cursor.fetchall():
                id_cat, nome, tipo = cat
                if tipo == "entrada":
                    lista_entradas.insert(tk.END, nome)
                else:
                    lista_saidas.insert(tk.END, nome)
                    
        carregar_categorias()
        
        # Frame para botões
        frame_botoes = ttk.Frame(janela)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Função para adicionar categoria
        def adicionar_categoria():
            tipo_var = tk.StringVar(value="entrada")
            
            # Janela de diálogo
            dialog = tk.Toplevel(janela)
            dialog.title("Nova Categoria")
            dialog.geometry("300x150")
            dialog.transient(janela)
            dialog.grab_set()
            
            # Frame
            frame = ttk.Frame(dialog, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Campos
            ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            nome_var = tk.StringVar()
            entry_nome = ttk.Entry(frame, textvariable=nome_var)
            entry_nome.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
            
            ttk.Label(frame, text="Tipo:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            rb_entrada = ttk.Radiobutton(frame, text="Entrada", variable=tipo_var, value="entrada")
            rb_entrada.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
            
            rb_saida = ttk.Radiobutton(frame, text="Saída", variable=tipo_var, value="saida")
            rb_saida.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
            
            # Botões
            frame_btns = ttk.Frame(frame)
            frame_btns.grid(row=3, column=0, columnspan=2, pady=10)
            
            def salvar():
                nome = nome_var.get().strip()
                tipo = tipo_var.get()
                
                if not nome:
                    messagebox.showerror("Erro", "O nome da categoria é obrigatório.", parent=dialog)
                    return
                    
                try:
                    self.cursor.execute("INSERT INTO categorias (nome, tipo) VALUES (?, ?)", (nome, tipo))
                    self.conn.commit()
                    dialog.destroy()
                    carregar_categorias()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Erro", "Já existe uma categoria com esse nome.", parent=dialog)
                except Exception as e:
                    messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}", parent=dialog)
            
            ttk.Button(frame_btns, text="Salvar", command=salvar).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame_btns, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        # Função para editar categoria
        def editar_categoria():
            # Verificar qual lista está selecionada
            lista_atual = None
            categoria = None
            tipo = None
            
            if lista_entradas.curselection():
                lista_atual = lista_entradas
                categoria = lista_entradas.get(lista_entradas.curselection())
                tipo = "entrada"
            elif lista_saidas.curselection():
                lista_atual = lista_saidas
                categoria = lista_saidas.get(lista_saidas.curselection())
                tipo = "saida"
                
            if not categoria:
                messagebox.showerror("Erro", "Selecione uma categoria para editar.", parent=janela)
                return
                
            # Obter ID da categoria
            self.cursor.execute("SELECT id FROM categorias WHERE nome = ? AND tipo = ?", (categoria, tipo))
            resultado = self.cursor.fetchone()
            if not resultado:
                messagebox.showerror("Erro", "Categoria não encontrada.", parent=janela)
                return
                
            id_categoria = resultado[0]
            
            # Janela de diálogo
            dialog = tk.Toplevel(janela)
            dialog.title("Editar Categoria")
            dialog.geometry("300x150")
            dialog.transient(janela)
            dialog.grab_set()
            
            # Frame
            frame = ttk.Frame(dialog, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Campos
            ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            nome_var = tk.StringVar(value=categoria)
            entry_nome = ttk.Entry(frame, textvariable=nome_var)
            entry_nome.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
            
            ttk.Label(frame, text="Tipo:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            tipo_var = tk.StringVar(value=tipo)
            rb_entrada = ttk.Radiobutton(frame, text="Entrada", variable=tipo_var, value="entrada")
            rb_entrada.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
            
            rb_saida = ttk.Radiobutton(frame, text="Saída", variable=tipo_var, value="saida")
            rb_saida.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
            
            # Botões
            frame_btns = ttk.Frame(frame)
            frame_btns.grid(row=3, column=0, columnspan=2, pady=10)
            
            def salvar():
                nome = nome_var.get().strip()
                novo_tipo = tipo_var.get()
                
                if not nome:
                    messagebox.showerror("Erro", "O nome da categoria é obrigatório.", parent=dialog)
                    return
                    
                try:
                    self.cursor.execute("UPDATE categorias SET nome = ?, tipo = ? WHERE id = ?", 
                                       (nome, novo_tipo, id_categoria))
                    self.conn.commit()
                    dialog.destroy()
                    carregar_categorias()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Erro", "Já existe uma categoria com esse nome.", parent=dialog)
                except Exception as e:
                    messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}", parent=dialog)
            
            ttk.Button(frame_btns, text="Salvar", command=salvar).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame_btns, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Função para excluir categoria
        def excluir_categoria():
            # Verificar qual lista está selecionada
            lista_atual = None
            categoria = None
            tipo = None
            
            if lista_entradas.curselection():
                lista_atual = lista_entradas
                categoria = lista_entradas.get(lista_entradas.curselection())
                tipo = "entrada"
            elif lista_saidas.curselection():
                lista_atual = lista_saidas
                categoria = lista_saidas.get(lista_saidas.curselection())
                tipo = "saida"
                
            if not categoria:
                messagebox.showerror("Erro", "Selecione uma categoria para excluir.", parent=janela)
                return
                
            # Obter ID da categoria
            self.cursor.execute("SELECT id FROM categorias WHERE nome = ? AND tipo = ?", (categoria, tipo))
            resultado = self.cursor.fetchone()
            if not resultado:
                messagebox.showerror("Erro", "Categoria não encontrada.", parent=janela)
                return
                
            id_categoria = resultado[0]
            
            # Verificar se há transações usando esta categoria
            self.cursor.execute("SELECT COUNT(*) FROM transacoes WHERE categoria_id = ?", (id_categoria,))
            total = self.cursor.fetchone()[0]
            
            if total > 0:
                resposta = messagebox.askyesno(
                    "Confirmação",
                    f"Existem {total} transações usando esta categoria. Ao excluí-la, essas transações ficarão sem categoria. Continuar?",
                    parent=janela
                )
                
                if not resposta:
                    return
            else:
                resposta = messagebox.askyesno(
                    "Confirmação",
                    "Tem certeza que deseja excluir esta categoria?",
                    parent=janela
                )
                
                if not resposta:
                    return
            
            try:
                # Remover referência nas transações
                self.cursor.execute("UPDATE transacoes SET categoria_id = NULL WHERE categoria_id = ?", (id_categoria,))
                
                # Excluir categoria
                self.cursor.execute("DELETE FROM categorias WHERE id = ?", (id_categoria,))
                self.conn.commit()
                
                carregar_categorias()
                messagebox.showinfo("Sucesso", "Categoria excluída com sucesso!", parent=janela)
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}", parent=janela)
        
        # Botões
        ttk.Button(frame_botoes, text="Nova Categoria", command=adicionar_categoria).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Editar", command=editar_categoria).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Excluir", command=excluir_categoria).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Fechar", command=janela.destroy).pack(side=tk.RIGHT, padx=5)
    
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

# Inicializar aplicativo
if __name__ == "__main__":
    
    root = tk.Tk()
    app = FluxoDeCaixaApp(root)
    root.mainloop()