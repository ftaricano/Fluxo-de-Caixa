from database import Database
from ui.main_window import MainWindow

def main():
    # Inicializar banco de dados
    db = Database()
    
    # Criar e iniciar janela principal
    app = MainWindow(db)
    app.run()

if __name__ == "__main__":
    main() 