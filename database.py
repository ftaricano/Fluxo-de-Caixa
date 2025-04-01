import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_path = os.path.join('data', 'fluxo_caixa.db')
        self.setup_database()

    def setup_database(self):
        """Configura o banco de dados e cria as tabelas necessárias"""
        if not os.path.exists('data'):
            os.makedirs('data')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Criar tabela de categorias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL
            )
        ''')

        # Criar tabela de transações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE NOT NULL,
                descricao TEXT NOT NULL,
                categoria_id INTEGER,
                valor REAL NOT NULL,
                tipo TEXT NOT NULL,
                FOREIGN KEY (categoria_id) REFERENCES categorias (id)
            )
        ''')

        # Inserir categorias padrão se não existirem
        cursor.execute("SELECT COUNT(*) FROM categorias")
        if cursor.fetchone()[0] == 0:
            categorias_padrao = [
                ('Salário', 'entrada'),
                ('Investimentos', 'entrada'),
                ('Outros', 'entrada'),
                ('Alimentação', 'saida'),
                ('Moradia', 'saida'),
                ('Transporte', 'saida'),
                ('Saúde', 'saida'),
                ('Educação', 'saida'),
                ('Lazer', 'saida'),
                ('Outros', 'saida')
            ]
            cursor.executemany("INSERT INTO categorias (nome, tipo) VALUES (?, ?)", categorias_padrao)

        conn.commit()
        conn.close()

    def get_categorias(self, tipo=None):
        """Retorna todas as categorias ou apenas as de um tipo específico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if tipo:
            cursor.execute("SELECT id, nome FROM categorias WHERE tipo = ?", (tipo,))
        else:
            cursor.execute("SELECT id, nome FROM categorias")
            
        categorias = cursor.fetchall()
        conn.close()
        return categorias

    def add_categoria(self, nome, tipo):
        """Adiciona uma nova categoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorias (nome, tipo) VALUES (?, ?)", (nome, tipo))
        conn.commit()
        conn.close()

    def delete_categoria(self, categoria_id):
        """Remove uma categoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
        conn.commit()
        conn.close()

    def add_transacao(self, data, descricao, categoria_id, valor, tipo):
        """Adiciona uma nova transação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transacoes (data, descricao, categoria_id, valor, tipo)
            VALUES (?, ?, ?, ?, ?)
        """, (data, descricao, categoria_id, valor, tipo))
        conn.commit()
        conn.close()

    def get_transacoes(self, mes=None, ano=None, tipo=None):
        """Retorna as transações com filtros opcionais"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT t.id, t.data, t.descricao, c.nome as categoria, t.valor, t.tipo
            FROM transacoes t
            LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE 1=1
        """
        params = []
        
        if mes:
            query += " AND strftime('%m', t.data) = ?"
            params.append(f"{mes:02d}")
        if ano:
            query += " AND strftime('%Y', t.data) = ?"
            params.append(str(ano))
        if tipo:
            query += " AND t.tipo = ?"
            params.append(tipo)
            
        query += " ORDER BY t.data DESC"
        
        cursor.execute(query, params)
        transacoes = cursor.fetchall()
        conn.close()
        return transacoes

    def update_transacao(self, transacao_id, data, descricao, categoria_id, valor, tipo):
        """Atualiza uma transação existente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transacoes 
            SET data = ?, descricao = ?, categoria_id = ?, valor = ?, tipo = ?
            WHERE id = ?
        """, (data, descricao, categoria_id, valor, tipo, transacao_id))
        conn.commit()
        conn.close()

    def delete_transacao(self, transacao_id):
        """Remove uma transação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacoes WHERE id = ?", (transacao_id,))
        conn.commit()
        conn.close()

    def get_fluxo_mensal(self, ano=None):
        """Retorna o fluxo de caixa mensal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                strftime('%Y-%m', data) as mes,
                SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END) as entradas,
                SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END) as saidas
            FROM transacoes
            WHERE 1=1
        """
        params = []
        
        if ano:
            query += " AND strftime('%Y', data) = ?"
            params.append(str(ano))
            
        query += " GROUP BY strftime('%Y-%m', data) ORDER BY mes DESC LIMIT 12"
        
        cursor.execute(query, params)
        fluxo = cursor.fetchall()
        conn.close()
        return fluxo

    def get_distribuicao_despesas(self, mes=None, ano=None):
        """Retorna a distribuição de despesas por categoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                c.nome as categoria,
                SUM(t.valor) as total
            FROM transacoes t
            JOIN categorias c ON t.categoria_id = c.id
            WHERE t.tipo = 'saida'
        """
        params = []
        
        if mes:
            query += " AND strftime('%m', t.data) = ?"
            params.append(f"{mes:02d}")
        if ano:
            query += " AND strftime('%Y', t.data) = ?"
            params.append(str(ano))
            
        query += " GROUP BY c.nome"
        
        cursor.execute(query, params)
        distribuicao = cursor.fetchall()
        conn.close()
        return distribuicao 