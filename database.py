# database.py

import mysql.connector
from datetime import datetime
import os
from db_config import DB_CONFIG # Importa le configurazioni del database

def get_db_connection():
    """
    Stabilisce e restituisce una connessione al database MySQL.
    Restituisce:
        conn: oggetto di connessione MySQL o None in caso di errore.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Errore di connessione al database: {err}")
        return None

def init_db():
    """
    Inizializza il database creando le tabelle necessarie se non esistono.
    Vengono create due tabelle:
    - anomalies: per memorizzare gli IP anomali rilevati.
    - analysis_history: per memorizzare lo storico delle analisi, inclusi i percorsi dei log e dei PDF.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Tabella per le anomalie (IP sospetti)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ip VARCHAR(255) NOT NULL,
                    attempts INT,
                    log_date DATETIME
                )
            """)
            # Tabella per lo storico delle analisi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    log_filepath VARCHAR(255) NOT NULL,
                    pdf_output_filepath VARCHAR(255) NOT NULL,
                    analysis_datetime DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Database MySQL inizializzato con successo.")
        except mysql.connector.Error as err:
            print(f"Errore durante l'inizializzazione del database: {err}")
        finally:
            cursor.close()
            conn.close()

def save_anomalies(anomalies, ip_counter):
    """
    Salva gli IP anomali rilevati nel database MySQL.
    Args:
        anomalies (list): Lista di IP anomali.
        ip_counter (Counter): Counter con il numero di tentativi per ogni IP.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        log_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            for ip in anomalies:
                attempts = ip_counter.get(ip, 0)
                cursor.execute(
                    "INSERT INTO anomalies (ip, attempts, log_date) VALUES (%s, %s, %s)",
                    (ip, attempts, log_date)
                )
            conn.commit()
            print("Anomalie salvate nel database MySQL.")
        except mysql.connector.Error as err:
            print(f"Errore durante il salvataggio delle anomalie: {err}")
        finally:
            cursor.close()
            conn.close()

def save_analysis_history(log_filepath, pdf_output_filepath):
    """
    Salva lo storico dell'analisi (percorso del log di input e del PDF di output)
    nel database MySQL.
    Args:
        log_filepath (str): Percorso del file di log analizzato.
        pdf_output_filepath (str): Percorso del PDF generato.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO analysis_history (log_filepath, pdf_output_filepath) VALUES (%s, %s)",
                (log_filepath, pdf_output_filepath)
            )
            conn.commit()
            print("Storico analisi salvato nel database MySQL.")
        except mysql.connector.Error as err:
            print(f"Errore durante il salvataggio dello storico analisi: {err}")
        finally:
            cursor.close()
            conn.close()

def get_analysis_history():
    """
    Recupera lo storico delle analisi dal database MySQL.
    Restituisce:
        history (list): Lista di dizionari, ciascuno rappresentante una riga della tabella analysis_history.
    """
    conn = get_db_connection()
    history = []
    if conn:
        cursor = conn.cursor(dictionary=True) # Restituisce i risultati come dizionari
        try:
            cursor.execute("SELECT * FROM analysis_history ORDER BY analysis_datetime DESC")
            history = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Errore durante il recupero dello storico analisi: {err}")
        finally:
            cursor.close()
            conn.close()
    return history