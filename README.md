# Gerenciador de Fluxo de Caixa 💰

## Descrição do Projeto

Este é um aplicativo de gerenciamento de fluxo de caixa desenvolvido em Python usando Tkinter para interface gráfica, SQLite para armazenamento de dados e Matplotlib para visualização de gráficos.

### Funcionalidades Principais

- 📊 Registro de transações de entrada e saída
- 📈 Visualização de gráficos de fluxo de caixa mensal
- 🍕 Distribuição de despesas por categoria
- 📑 Gerenciamento de categorias personalizadas
- 📥 Importação de dados via planilha Excel
- 💾 Persistência de dados em banco SQLite

## Requisitos

- Python 3.8+
- Bibliotecas:
  - tkinter
  - sqlite3
  - matplotlib
  - pandas
  - openpyxl

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/gerenciador-fluxo-caixa.git
cd gerenciador-fluxo-caixa
```

2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install matplotlib pandas openpyxl
```

## Como Usar

### Iniciando o Aplicativo
```bash
python fluxo_caixa.py
```

### Funcionalidades

#### Adicionar Transações
- Clique em "+ Entrada" ou "+ Saída"
- Preencha os dados: data, descrição, categoria e valor
- Salve a transação

#### Gerenciar Categorias
- Acesse "Gerenciar Categorias"
- Adicione, edite ou exclua categorias de entrada e saída

#### Filtrar Transações
- Filtre por mês, ano ou tipo de transação
- Visualize o saldo e gráficos atualizados

#### Importar Planilha Excel
- Clique em "Importar Excel"
- Selecione uma planilha com as colunas:
  - Tipo
  - Data
  - Lançamento
  - Valor
  - Categoria
  - Lançamento Original
  - REF

## Estrutura do Projeto

```
gerenciador-fluxo-caixa/
│
├── fluxo_caixa.py      # Arquivo principal
├── data/               # Diretório de dados
│   └── fluxo_caixa.db  # Banco de dados SQLite
└── README.md           # Este arquivo
```

## Personalização

### Categorias Padrão
O aplicativo já vem com categorias padrão:

Entradas:
- Vendas
- Serviços
- Investimentos
- Outras Receitas

Saídas:
- Materiais
- Salários
- Aluguel
- Impostos
- Fornecedores
- Despesas Operacionais
- Outras Despesas

## Contribuições

1. Faça um fork do projeto
2. Crie sua branch de feature (`git checkout -b feature/novaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/novaFeature`)
5. Abra um Pull Request

## Licença

[Especifique a licença - por exemplo, MIT]

## Contato

[Seu nome ou informações de contato]

## Capturas de Tela

[Adicione algumas capturas de tela do aplicativo mostrando suas principais funcionalidades]

## Próximos Passos

- [ ] Implementar exportação de relatórios
- [ ] Adicionar gráficos de projeção
- [ ] Melhorar validações de entrada
- [ ] Criar modo de visualização de relatórios
