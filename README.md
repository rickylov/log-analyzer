# Progetto Lovato – Analisi Log con MySQL

Questo progetto sviluppato in Python consente di analizzare file di log, salvarne i risultati in un database MySQL e generare report automatici.

## Requisiti di sistema

- Ubuntu Linux (22.04 o superiore consigliato)
- Python 3.10 o superiore
- MySQL Server
- pip (Python package manager)

## 1. Installazione delle dipendenze Python

Apri un terminale nella directory del progetto ed esegui:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Installazione e configurazione di MySQL

### Installazione

```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

### Configurazione utente e database

1. Accedi a MySQL:

```bash
sudo mysql
```

2. Crea un database e un utente:

```sql
CREATE DATABASE progetto_log;
CREATE USER 'loguser'@'localhost' IDENTIFIED BY 'logpass';
GRANT ALL PRIVILEGES ON progetto_log.* TO 'loguser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

3. [IMPORTANTE] Modifica il file `db_config.py` con questi dati di accesso oppure con quelli inseriti precedentemente:

```python
# db_config.py
DB_CONFIG = {
    'host': 'localhost',
    'user': 'loguser',
    'password': 'logpass',
    'database': 'progetto_log'
}
```

## 3. Inizializzazione del Database

Il file `database.py`  contiene la logica per creare le tabelle. Puoi eseguire direttamente:

```bash
python3 database.py
```

Assicurati che la configurazione in `db_config.py` sia corretta prima.

## 4. Esecuzione del progetto

Per avviare l'analisi:

```bash
python3 main.py
```

Verifica nel terminale o nei file generati i risultati dell'elaborazione e dell'inserimento nel database.

## 5. File utili

- `main.py` – Punto di ingresso principale
- `database.py` – Connessione e inizializzazione database
- `log_parser.py`, `analyzer.py` – Parsing e analisi dei log
- `report_generator.py` – Generazione report finale

---

## Contatti

Progetto realizzato da Lovato Riccardo per il corso di Python.
