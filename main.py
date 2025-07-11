### main

import tkinter as tk
from gui import SecurityLogAnalyzerGUI   # Importa la classe GUI principale
from database import init_db             # Importa la funzione per inizializzare il database

if __name__ == "__main__":
    # Inizializza il database (crea le tabelle se non esistono)
    init_db()

    # Crea la finestra principale Tkinter
    root = tk.Tk()
    # Istanzia e avvia l'interfaccia grafica dell'analizzatore di log
    app = SecurityLogAnalyzerGUI(root)
    # Avvia il loop principale della GUI
    root.mainloop()


