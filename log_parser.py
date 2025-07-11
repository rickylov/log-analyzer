def parse_log(filepath):
    """
    Analizza un file di log e restituisce una lista di eventi di accesso fallito.
    Ogni evento è rappresentato da un dizionario con chiavi 'ip' e 'timestamp'.

    Args:
        filepath (str): Percorso del file di log da analizzare.

    Returns:
        list: Lista di dizionari, ciascuno con 'ip' e 'timestamp' di un tentativo fallito.
    """
    entries = []
    with open(filepath, 'r') as file:
        for line in file:
            # Considera solo le righe che contengono "Failed password"
            if "Failed password" in line:
                parts = line.split()
                ip = parts[-4]  # Estrae l'IP dalla posizione attesa nella riga
                timestamp = " ".join(parts[0:3])  # Estrae il timestamp (es: "Jan 10 12:34:56")
                entries.append({"ip": ip, "timestamp": timestamp})
    return entries