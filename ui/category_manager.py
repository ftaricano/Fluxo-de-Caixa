import tkinter as tk
from tkinter import ttk, messagebox

class CategoryManager:
    def __init__(self, parent, db):
        self.window = tk.Toplevel(parent)
        self.window.title("Gerenciador de Categorias")
        self.window.geometry("600x400")
        self.window.resizable(False, False)
        self.window.configure(bg='#f0f0f0')
        
        self.db = db
        
        self.criar_interface()
        self.carregar_categorias()
        
    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(
            main_frame,
            text="Gerenciador de Categorias",
            font=('Helvetica', 16, 'bold')
        )
        titulo.pack(pady=(0, 20))
        
        # Frame para as listas
        listas_frame = ttk.Frame(main_frame)
        listas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de Entradas
        entrada_frame = ttk.LabelFrame(listas_frame, text="Categorias de Entrada", padding="10")
        entrada_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.entrada_tree = ttk.Treeview(
            entrada_frame,
            columns=('id', 'nome'),
            show='headings',
            height=10
        )
        self.entrada_tree.heading('id', text='ID')
        self.entrada_tree.heading('nome', text='Nome')
        self.entrada_tree.column('id', width=50)
        self.entrada_tree.column('nome', width=150)
        self.entrada_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        entrada_scroll = ttk.Scrollbar(entrada_frame, orient=tk.VERTICAL, command=self.entrada_tree.yview)
        entrada_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.entrada_tree.configure(yscrollcommand=entrada_scroll.set)
        
        # Lista de Saídas
        saida_frame = ttk.LabelFrame(listas_frame, text="Categorias de Saída", padding="10")
        saida_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.saida_tree = ttk.Treeview(
            saida_frame,
            columns=('id', 'nome'),
            show='headings',
            height=10
        )
        self.saida_tree.heading('id', text='ID')
        self.saida_tree.heading('nome', text='Nome')
        self.saida_tree.column('id', width=50)
        self.saida_tree.column('nome', width=150)
        self.saida_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        saida_scroll = ttk.Scrollbar(saida_frame, orient=tk.VERTICAL, command=self.saida_tree.yview)
        saida_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.saida_tree.configure(yscrollcommand=saida_scroll.set)
        
        # Frame para botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botões
        ttk.Button(
            botoes_frame,
            text="Adicionar Entrada",
            command=lambda: self.adicionar_categoria('entrada')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Adicionar Saída",
            command=lambda: self.adicionar_categoria('saida')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Editar",
            command=self.editar_categoria
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Excluir",
            command=self.excluir_categoria
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Fechar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Centralizar janela
        self.window.transient(self.window.master)
        self.window.grab_set()
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
    def carregar_categorias(self):
        # Limpar listas
        for item in self.entrada_tree.get_children():
            self.entrada_tree.delete(item)
        for item in self.saida_tree.get_children():
            self.saida_tree.delete(item)
        
        # Carregar categorias de entrada
        categorias_entrada = self.db.get_categorias('entrada')
        for cat_id, cat_nome in categorias_entrada:
            self.entrada_tree.insert('', 'end', values=(cat_id, cat_nome))
        
        # Carregar categorias de saída
        categorias_saida = self.db.get_categorias('saida')
        for cat_id, cat_nome in categorias_saida:
            self.saida_tree.insert('', 'end', values=(cat_id, cat_nome))
            
    def adicionar_categoria(self, tipo):
        dialog = tk.Toplevel(self.window)
        dialog.title(f"Nova Categoria de {'Entrada' if tipo == 'entrada' else 'Saída'}")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campo de nome
        ttk.Label(main_frame, text="Nome:").pack(pady=5)
        nome_entry = ttk.Entry(main_frame, width=30)
        nome_entry.pack(pady=5)
        
        def salvar():
            nome = nome_entry.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Digite um nome para a categoria")
                return
            
            try:
                self.db.add_categoria(nome, tipo)
                self.carregar_categorias()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar categoria: {str(e)}")
        
        # Botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            botoes_frame,
            text="Salvar",
            command=salvar,
            style='Accent.TButton'
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Cancelar",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
    def editar_categoria(self):
        # Verificar seleção
        entrada_selecionada = self.entrada_tree.selection()
        saida_selecionada = self.saida_tree.selection()
        
        if not entrada_selecionada and not saida_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma categoria para editar")
            return
        
        # Identificar tipo e item selecionado
        if entrada_selecionada:
            item = self.entrada_tree.item(entrada_selecionada[0])
            tipo = 'entrada'
        else:
            item = self.saida_tree.item(saida_selecionada[0])
            tipo = 'saida'
        
        # Criar diálogo de edição
        dialog = tk.Toplevel(self.window)
        dialog.title(f"Editar Categoria de {'Entrada' if tipo == 'entrada' else 'Saída'}")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campo de nome
        ttk.Label(main_frame, text="Nome:").pack(pady=5)
        nome_entry = ttk.Entry(main_frame, width=30)
        nome_entry.insert(0, item['values'][1])
        nome_entry.pack(pady=5)
        
        def salvar():
            nome = nome_entry.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Digite um nome para a categoria")
                return
            
            try:
                self.db.update_categoria(item['values'][0], nome)
                self.carregar_categorias()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar categoria: {str(e)}")
        
        # Botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            botoes_frame,
            text="Salvar",
            command=salvar,
            style='Accent.TButton'
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Cancelar",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
    def excluir_categoria(self):
        # Verificar seleção
        entrada_selecionada = self.entrada_tree.selection()
        saida_selecionada = self.saida_tree.selection()
        
        if not entrada_selecionada and not saida_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma categoria para excluir")
            return
        
        # Confirmar exclusão
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta categoria?"):
            return
        
        try:
            if entrada_selecionada:
                item = self.entrada_tree.item(entrada_selecionada[0])
            else:
                item = self.saida_tree.item(saida_selecionada[0])
            
            self.db.delete_categoria(item['values'][0])
            self.carregar_categorias()
            messagebox.showinfo("Sucesso", "Categoria excluída com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir categoria: {str(e)}") 