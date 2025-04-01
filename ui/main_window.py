import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkthemes

from .transaction_form import TransactionForm
from .category_manager import CategoryManager
from utils.excel_importer import importar_excel, validar_arquivo_excel
from utils.graph_utils import criar_grafico_fluxo_mensal, criar_grafico_distribuicao

class MainWindow:
    def __init__(self, db):
        self.window = tk.Tk()
        self.window.title("Fluxo de Caixa")
        self.window.geometry("1200x700")
        self.window.configure(bg='#f0f0f0')
        
        self.db = db
        self.setup_styles()
        self.criar_interface()
        
    def setup_styles(self):
        """Configura os estilos da interface"""
        style = ttkthemes.ThemedStyle(self.window)
        style.set_theme("clam")
        
        # Configurar cores e estilos
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('Accent.TButton', background='#3498db', foreground='white')
        style.configure('Treeview', font=('Helvetica', 10))
        style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
        style.configure('TCombobox', font=('Helvetica', 10))
        
    def criar_interface(self):
        """Cria a interface principal"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame superior (resumo e botões)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Resumo financeiro
        resumo_frame = ttk.LabelFrame(top_frame, text="Resumo Financeiro", padding="10")
        resumo_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.saldo_label = ttk.Label(
            resumo_frame,
            text="Saldo Atual: R$ 0,00",
            font=('Helvetica', 12, 'bold')
        )
        self.saldo_label.pack(side=tk.LEFT, padx=10)
        
        self.entradas_label = ttk.Label(
            resumo_frame,
            text="Total Entradas: R$ 0,00",
            font=('Helvetica', 12),
            foreground='#2ecc71'
        )
        self.entradas_label.pack(side=tk.LEFT, padx=10)
        
        self.saidas_label = ttk.Label(
            resumo_frame,
            text="Total Saídas: R$ 0,00",
            font=('Helvetica', 12),
            foreground='#e74c3c'
        )
        self.saidas_label.pack(side=tk.LEFT, padx=10)
        
        # Botões de ação
        botoes_frame = ttk.Frame(top_frame)
        botoes_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            botoes_frame,
            text="+ Nova Entrada",
            command=lambda: self.nova_transacao('entrada'),
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="+ Nova Saída",
            command=lambda: self.nova_transacao('saida'),
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Gerenciar Categorias",
            command=self.abrir_gerenciador_categorias
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Importar Excel",
            command=self.importar_excel
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame para filtros e tabela
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Filtros
        filtros_frame = ttk.LabelFrame(content_frame, text="Filtros", padding="10")
        filtros_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Mês
        ttk.Label(filtros_frame, text="Mês:").pack(side=tk.LEFT, padx=5)
        self.mes_combo = ttk.Combobox(
            filtros_frame,
            values=[f"{i:02d}" for i in range(1, 13)],
            width=5,
            state="readonly"
        )
        self.mes_combo.pack(side=tk.LEFT, padx=5)
        self.mes_combo.set(datetime.now().strftime("%m"))
        
        # Ano
        ttk.Label(filtros_frame, text="Ano:").pack(side=tk.LEFT, padx=5)
        self.ano_combo = ttk.Combobox(
            filtros_frame,
            values=[str(i) for i in range(2020, datetime.now().year + 1)],
            width=5,
            state="readonly"
        )
        self.ano_combo.pack(side=tk.LEFT, padx=5)
        self.ano_combo.set(str(datetime.now().year))
        
        # Tipo
        ttk.Label(filtros_frame, text="Tipo:").pack(side=tk.LEFT, padx=5)
        self.tipo_combo = ttk.Combobox(
            filtros_frame,
            values=["Todos", "Entradas", "Saídas"],
            width=10,
            state="readonly"
        )
        self.tipo_combo.pack(side=tk.LEFT, padx=5)
        self.tipo_combo.set("Todos")
        
        # Botão aplicar filtros
        ttk.Button(
            filtros_frame,
            text="Aplicar Filtros",
            command=self.aplicar_filtros
        ).pack(side=tk.LEFT, padx=20)
        
        # Tabela de transações
        tabela_frame = ttk.LabelFrame(content_frame, text="Transações", padding="10")
        tabela_frame.pack(fill=tk.BOTH, expand=True)
        
        # Criar tabela
        self.tabela = ttk.Treeview(
            tabela_frame,
            columns=('data', 'descricao', 'categoria', 'valor', 'tipo'),
            show='headings',
            height=10
        )
        
        # Configurar colunas
        self.tabela.heading('data', text='Data')
        self.tabela.heading('descricao', text='Descrição')
        self.tabela.heading('categoria', text='Categoria')
        self.tabela.heading('valor', text='Valor')
        self.tabela.heading('tipo', text='Tipo')
        
        self.tabela.column('data', width=100)
        self.tabela.column('descricao', width=300)
        self.tabela.column('categoria', width=150)
        self.tabela.column('valor', width=100)
        self.tabela.column('tipo', width=100)
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(tabela_frame, orient=tk.VERTICAL, command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar elementos
        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para gráficos
        graficos_frame = ttk.Frame(main_frame)
        graficos_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Gráfico de fluxo mensal
        fluxo_frame = ttk.LabelFrame(graficos_frame, text="Fluxo de Caixa Mensal", padding="10")
        fluxo_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.fig_fluxo = Figure(figsize=(6, 4), facecolor='#f0f0f0')
        self.canvas_fluxo = FigureCanvasTkAgg(self.fig_fluxo, master=fluxo_frame)
        self.canvas_fluxo.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Gráfico de distribuição
        dist_frame = ttk.LabelFrame(graficos_frame, text="Distribuição de Despesas", padding="10")
        dist_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.fig_dist = Figure(figsize=(6, 4), facecolor='#f0f0f0')
        self.canvas_dist = FigureCanvasTkAgg(self.fig_dist, master=dist_frame)
        self.canvas_dist.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configurar eventos
        self.tabela.bind('<Double-1>', self.editar_transacao)
        
        # Carregar dados iniciais
        self.carregar_transacoes()
        self.atualizar_graficos()
        
    def nova_transacao(self, tipo):
        """Abre o formulário para nova transação"""
        form = TransactionForm(self.window, self.db, tipo)
        self.window.wait_window(form.window)
        
        if form.resultado:
            self.carregar_transacoes()
            self.atualizar_graficos()
            
    def editar_transacao(self, event):
        """Edita a transação selecionada"""
        item = self.tabela.selection()
        if not item:
            return
            
        transacao = self.tabela.item(item[0])['values']
        tipo = 'entrada' if transacao[4] == 'Entrada' else 'saida'
        
        form = TransactionForm(self.window, self.db, tipo, transacao)
        self.window.wait_window(form.window)
        
        if form.resultado:
            self.carregar_transacoes()
            self.atualizar_graficos()
            
    def abrir_gerenciador_categorias(self):
        """Abre o gerenciador de categorias"""
        manager = CategoryManager(self.window, self.db)
        self.window.wait_window(manager.window)
        
    def importar_excel(self):
        """Importa dados de um arquivo Excel"""
        arquivo = filedialog.askopenfilename(
            title="Selecionar arquivo Excel",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls")]
        )
        
        if not arquivo:
            return
            
        if not validar_arquivo_excel(arquivo):
            messagebox.showerror("Erro", "Arquivo Excel inválido")
            return
            
        sucesso, mensagem = importar_excel(arquivo, self.db)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.carregar_transacoes()
            self.atualizar_graficos()
        else:
            messagebox.showerror("Erro", mensagem)
            
    def aplicar_filtros(self):
        """Aplica os filtros selecionados"""
        self.carregar_transacoes()
        self.atualizar_graficos()
        
    def carregar_transacoes(self):
        """Carrega as transações na tabela"""
        # Limpar tabela
        for item in self.tabela.get_children():
            self.tabela.delete(item)
            
        # Obter filtros
        mes = int(self.mes_combo.get()) if self.mes_combo.get() else None
        ano = int(self.ano_combo.get()) if self.ano_combo.get() else None
        tipo = self.tipo_combo.get().lower() if self.tipo_combo.get() != "Todos" else None
        
        # Carregar transações
        transacoes = self.db.get_transacoes(mes, ano, tipo)
        
        # Inserir na tabela
        for t in transacoes:
            self.tabela.insert('', 'end', values=(
                t[1],  # data
                t[2],  # descrição
                t[3],  # categoria
                f"R$ {t[4]:,.2f}",  # valor
                'Entrada' if t[5] == 'entrada' else 'Saída'  # tipo
            ))
            
        # Atualizar resumo
        self.atualizar_resumo()
        
    def atualizar_resumo(self):
        """Atualiza o resumo financeiro"""
        # Obter filtros
        mes = int(self.mes_combo.get()) if self.mes_combo.get() else None
        ano = int(self.ano_combo.get()) if self.ano_combo.get() else None
        
        # Carregar transações do mês
        transacoes = self.db.get_transacoes(mes, ano)
        
        # Calcular totais
        total_entradas = sum(t[4] for t in transacoes if t[5] == 'entrada')
        total_saidas = sum(t[4] for t in transacoes if t[5] == 'saida')
        saldo = total_entradas - total_saidas
        
        # Atualizar labels
        self.saldo_label.config(
            text=f"Saldo Atual: R$ {saldo:,.2f}",
            foreground='#2ecc71' if saldo >= 0 else '#e74c3c'
        )
        self.entradas_label.config(text=f"Total Entradas: R$ {total_entradas:,.2f}")
        self.saidas_label.config(text=f"Total Saídas: R$ {total_saidas:,.2f}")
        
    def atualizar_graficos(self):
        """Atualiza os gráficos"""
        # Obter filtros
        ano = int(self.ano_combo.get()) if self.ano_combo.get() else None
        
        # Atualizar gráfico de fluxo mensal
        dados_fluxo = self.db.get_fluxo_mensal(ano)
        criar_grafico_fluxo_mensal(self.fig_fluxo, dados_fluxo, ano)
        self.canvas_fluxo.draw()
        
        # Atualizar gráfico de distribuição
        dados_dist = self.db.get_distribuicao_despesas(
            int(self.mes_combo.get()) if self.mes_combo.get() else None,
            ano
        )
        criar_grafico_distribuicao(self.fig_dist, dados_dist)
        self.canvas_dist.draw()
        
    def run(self):
        """Inicia a aplicação"""
        self.window.mainloop() 