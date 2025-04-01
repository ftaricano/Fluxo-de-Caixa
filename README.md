# Gerenciador de Fluxo de Caixa

Uma aplicação desktop para gerenciamento de fluxo de caixa, desenvolvida em Python com interface gráfica usando Tkinter.

## Funcionalidades

- Cadastro de entradas e saídas financeiras
- Categorização de transações
- Visualização de saldo atual
- Gráficos de fluxo mensal e distribuição de despesas
- Filtros por mês, ano e tipo de transação
- Importação de dados via Excel
- Gerenciamento de categorias

## Requisitos

- Python 3.8 ou superior
- Bibliotecas listadas em `requirements.txt`

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/fluxo-de-caixa.git
cd fluxo-de-caixa
```

2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Para iniciar a aplicação, execute:
```bash
python main.py
```

### Principais funcionalidades

1. **Adicionar Transação**
   - Clique em "+ Nova Entrada" ou "+ Nova Saída"
   - Preencha os campos do formulário
   - Clique em "Salvar"

2. **Visualizar Gráficos**
   - O gráfico de fluxo mensal mostra entradas e saídas dos últimos 12 meses
   - O gráfico de distribuição mostra a proporção das despesas por categoria

3. **Filtrar Dados**
   - Use os filtros no topo da tela para filtrar por mês, ano e tipo de transação
   - Os gráficos e a tabela serão atualizados automaticamente

4. **Gerenciar Categorias**
   - Clique em "Gerenciar Categorias" para adicionar, editar ou excluir categorias
   - As categorias são separadas entre entradas e saídas

5. **Importar Dados**
   - Clique em "Importar Excel" para importar transações de um arquivo Excel
   - O arquivo deve seguir o formato especificado na janela de importação

## Estrutura do Projeto

```
fluxo-de-caixa/
├── data/               # Diretório para armazenar o banco de dados
├── ui/                 # Interface do usuário
│   ├── __init__.py
│   ├── main_window.py  # Janela principal
│   ├── transaction_form.py  # Formulário de transações
│   └── category_manager.py  # Gerenciador de categorias
├── utils/             # Utilitários
│   ├── __init__.py
│   ├── graph_utils.py # Funções para gráficos
│   └── excel_importer.py # Importação de Excel
├── database.py        # Gerenciamento do banco de dados
├── main.py           # Ponto de entrada da aplicação
├── requirements.txt  # Dependências do projeto
└── README.md        # Este arquivo
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
