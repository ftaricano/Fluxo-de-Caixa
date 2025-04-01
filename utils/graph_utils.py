import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def criar_grafico_fluxo_mensal(fig, dados, ano_atual):
    """Cria o gráfico de fluxo mensal"""
    plt.clf()
    ax = fig.add_subplot(111)
    
    if not dados:
        ax.text(0.5, 0.5, 'Nenhum dado disponível', 
                horizontalalignment='center', 
                verticalalignment='center',
                transform=ax.transAxes)
        return
    
    # Preparar dados
    meses = [d[0] for d in dados]
    entradas = [d[1] for d in dados]
    saidas = [d[2] for d in dados]
    
    # Criar barras
    x = np.arange(len(meses))
    width = 0.35
    
    ax.bar(x - width/2, entradas, width, label='Entradas', color='#2ecc71', alpha=0.7)
    ax.bar(x + width/2, saidas, width, label='Saídas', color='#e74c3c', alpha=0.7)
    
    # Configurar eixos
    ax.set_xlabel('Mês')
    ax.set_ylabel('Valor (R$)')
    ax.set_title(f'Fluxo de Caixa Mensal - {ano_atual}')
    ax.set_xticks(x)
    ax.set_xticklabels([m.split('-')[1] for m in meses], rotation=45)
    
    # Adicionar grid e legenda
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Adicionar valores nas barras
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'R$ {height:,.0f}',
                   ha='center', va='bottom')
    
    add_value_labels(ax.patches)
    
    # Ajustar layout
    fig.tight_layout()

def criar_grafico_distribuicao(fig, dados):
    """Cria o gráfico de distribuição de despesas"""
    plt.clf()
    ax = fig.add_subplot(111)
    
    if not dados:
        ax.text(0.5, 0.5, 'Nenhum dado disponível', 
                horizontalalignment='center', 
                verticalalignment='center',
                transform=ax.transAxes)
        return
    
    # Preparar dados
    categorias = [d[0] for d in dados]
    valores = [d[1] for d in dados]
    
    # Cores para o gráfico
    cores = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f', '#9b59b6', 
             '#1abc9c', '#e67e22', '#34495e', '#7f8c8d', '#16a085']
    
    # Criar gráfico de pizza
    patches, texts, autotexts = ax.pie(valores, labels=categorias, 
                                     autopct='%1.1f%%', colors=cores)
    
    # Configurar título
    ax.set_title('Distribuição de Despesas por Categoria')
    
    # Ajustar layout
    fig.tight_layout() 