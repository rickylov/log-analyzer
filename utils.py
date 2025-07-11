# utils.py
import os
import mysql.connector
from db_config import DB_CONFIG # Importa le configurazioni del database

def reset_all():
    """
    Elimina il database MySQL e tutti i report PDF generati.
    Poi ricrea le tabelle vuote nel database.
    """
    # Elimina i PDF generati nella cartella 'output'
    output_dir = "output"
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            if filename.endswith(".pdf") or filename.endswith(".png"): # Elimina anche i grafici PNG
                filepath = os.path.join(output_dir, filename)
                try:
                    os.remove(filepath)
                    print(f"🗑️ Eliminato file: {filepath}")
                except Exception as e:
                    print(f"Errore durante l'eliminazione di {filepath}: {e}")
    
    # Connessione al database per eliminare le tabelle
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Elimina le tabelle se esistono
        cursor.execute("DROP TABLE IF EXISTS anomalies")
        cursor.execute("DROP TABLE IF EXISTS analysis_history")
        conn.commit()
        print("🗑️ Tabelle database MySQL eliminate.")
        
    except mysql.connector.Error as err:
        print(f"Errore durante il reset del database: {err}")
    finally:
        # Chiude il cursore e la connessione se sono stati aperti
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
    # Ricrea database vuoto (chiamando init_db)
    from database import init_db
    init_db()
    print("🔁 Sistema resettato e pronto.")

