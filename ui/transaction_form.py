import tkinter as tk
from tkinter import ttk
from datetime import datetime
import tkcalendar

class TransactionForm:
    def __init__(self, parent, db, tipo, transacao=None):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Nova {'Entrada' if tipo == 'entrada' else 'Saída'}")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        self.window.configure(bg='#f0f0f0')
        
        self.db = db
        self.tipo = tipo
        self.transacao = transacao
        self.resultado = None
        
        self.criar_interface()
        
    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(
            main_frame,
            text=f"Nova {'Entrada' if self.tipo == 'entrada' else 'Saída'}",
            font=('Helvetica', 16, 'bold')
        )
        titulo.pack(pady=(0, 20))
        
        # Frame para os campos
        campos_frame = ttk.Frame(main_frame)
        campos_frame.pack(fill=tk.BOTH, expand=True)
        
        # Data
        ttk.Label(campos_frame, text="Data:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.data_entry = tkcalendar.DateEntry(
            campos_frame,
            width=12,
            background='#3498db',
            foreground='white',
            borderwidth=2
        )
        self.data_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Descrição
        ttk.Label(campos_frame, text="Descrição:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.descricao_entry = ttk.Entry(campos_frame, width=30)
        self.descricao_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Categoria
        ttk.Label(campos_frame, text="Categoria:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.categoria_combo = ttk.Combobox(campos_frame, width=27, state="readonly")
        self.categoria_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Carregar categorias
        categorias = self.db.get_categorias(self.tipo)
        self.categoria_combo['values'] = [cat[1] for cat in categorias]
        
        # Valor
        ttk.Label(campos_frame, text="Valor:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.valor_entry = ttk.Entry(campos_frame, width=30)
        self.valor_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Se for edição, preencher campos
        if self.transacao:
            self.data_entry.set_date(datetime.strptime(self.transacao[1], '%Y-%m-%d'))
            self.descricao_entry.insert(0, self.transacao[2])
            self.categoria_combo.set(self.transacao[3])
            self.valor_entry.insert(0, str(self.transacao[4]))
        
        # Frame para botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botões
        ttk.Button(
            botoes_frame,
            text="Salvar",
            command=self.salvar,
            style='Accent.TButton'
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Cancelar",
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
        
    def salvar(self):
        try:
            data = self.data_entry.get_date()
            descricao = self.descricao_entry.get()
            categoria = self.categoria_combo.get()
            valor = float(self.valor_entry.get().replace(',', '.'))
            
            if not descricao or not categoria or valor <= 0:
                raise ValueError("Preencha todos os campos corretamente")
            
            # Encontrar ID da categoria
            categorias = self.db.get_categorias(self.tipo)
            categoria_id = None
            for cat_id, cat_nome in categorias:
                if cat_nome == categoria:
                    categoria_id = cat_id
                    break
            
            if not categoria_id:
                raise ValueError("Categoria inválida")
            
            if self.transacao:
                # Atualizar transação existente
                self.db.update_transacao(
                    self.transacao[0],
                    data,
                    descricao,
                    categoria_id,
                    valor,
                    self.tipo
                )
            else:
                # Adicionar nova transação
                self.db.add_transacao(
                    data,
                    descricao,
                    categoria_id,
                    valor,
                    self.tipo
                )
            
            self.resultado = True
            self.window.destroy()
            
        except ValueError as e:
            tk.messagebox.showerror("Erro", str(e))
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}") 