from sklearn.ensemble import IsolationForest


def detect_anomalies(summary):
    """
    Rileva IP anomali utilizzando Isolation Forest.
    Analizza la frequenza degli IP e la distribuzione oraria degli eventi.

    Args:
        summary (dict): Dizionario con 'ip_counter' e 'hourly_counter'.

    Returns:
        list: Lista di IP rilevati come anomali.
    """
    ip_counter = summary["ip_counter"]
    hourly_counter = summary["hourly_counter"]

    data = []   # Lista delle feature per ogni IP (numero tentativi, ora media)
    ips = []    # Lista degli IP corrispondenti

    for ip, count in ip_counter.items():
        total_attempts = sum(hourly_counter.values())
        if total_attempts == 0:
            ora_media = 0
        else:
            # Calcola l'ora media ponderata degli eventi
            ora_media = sum(hour * freq for hour, freq in hourly_counter.items()) / total_attempts
        data.append([count, ora_media])
        ips.append(ip)

    if not data:
        return []  # Nessun dato da analizzare

    try:
        # Crea e addestra il modello Isolation Forest per rilevare outlier
        model = IsolationForest(contamination=0.2, random_state=42)
        preds = model.fit_predict(data)
        # Gli IP con predizione -1 sono considerati anomali
        anomalous_ips = [ip for ip, pred in zip(ips, preds) if pred == -1]
        return anomalous_ips
    except Exception as e:
        print("Errore nel modello:", e)
        return []  # Fallback in caso di errore
