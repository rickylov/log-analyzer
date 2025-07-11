from collections import Counter
from datetime import datetime

def analyze_events(entries):
    """
    Analizza una lista di eventi di log e restituisce:
    - un Counter con la frequenza di ogni IP
    - un Counter con la frequenza degli eventi per ogni ora del giorno

    Args:
        entries (list): Lista di dizionari, ciascuno rappresentante un evento di log con chiavi 'ip' e 'timestamp'.

    Returns:
        dict: Dizionario con due Counter: 'ip_counter' e 'hourly_counter'
    """
    ip_counter = Counter()        # Conta le occorrenze di ogni IP
    hourly_counter = Counter()    # Conta gli eventi per ogni ora

    for entry in entries:
        ip = entry["ip"]
        ip_counter[ip] += 1      # Incrementa il conteggio per l'IP

        try:
            # Estrae l'ora dal timestamp (formato: "Mese Giorno Ora:Minuti:Secondi")
            hour = datetime.strptime(entry["timestamp"], "%b %d %H:%M:%S").hour
            hourly_counter[hour] += 1  # Incrementa il conteggio per quell'ora
        except ValueError:
            # Se il timestamp non è nel formato atteso, ignora l'errore
            pass

    return {
        "ip_counter": ip_counter,
        "hourly_counter": hourly_counter
    }
        