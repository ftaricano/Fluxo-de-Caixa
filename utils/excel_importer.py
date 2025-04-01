import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

def importar_excel(arquivo, db):
    """Importa dados de um arquivo Excel para o banco de dados"""
    try:
        # Ler o arquivo Excel
        df = pd.read_excel(arquivo)
        
        # Verificar colunas obrigatórias
        colunas_obrigatorias = ['Data', 'Descrição', 'Categoria', 'Valor', 'Tipo']
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltantes:
            raise ValueError(f"Colunas obrigatórias faltando: {', '.join(colunas_faltantes)}")
        
        # Converter tipos de dados
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        
        # Validar dados
        if df['Valor'].isna().any():
            raise ValueError("Valores inválidos encontrados na coluna 'Valor'")
        
        if not df['Tipo'].isin(['entrada', 'saida']).all():
            raise ValueError("Tipo deve ser 'entrada' ou 'saida'")
        
        # Inserir dados no banco
        for _, row in df.iterrows():
            # Verificar se a categoria existe
            categorias = db.get_categorias()
            categoria_id = None
            for cat_id, cat_nome in categorias:
                if cat_nome == row['Categoria']:
                    categoria_id = cat_id
                    break
            
            if not categoria_id:
                raise ValueError(f"Categoria não encontrada: {row['Categoria']}")
            
            # Inserir transação
            db.add_transacao(
                data=row['Data'],
                descricao=row['Descrição'],
                categoria_id=categoria_id,
                valor=float(row['Valor']),
                tipo=row['Tipo']
            )
        
        return True, "Dados importados com sucesso!"
        
    except Exception as e:
        return False, f"Erro ao importar dados: {str(e)}"

def validar_arquivo_excel(arquivo):
    """Valida se o arquivo é um Excel válido"""
    try:
        # Tentar ler o arquivo
        pd.read_excel(arquivo)
        return True
    except:
        return False 