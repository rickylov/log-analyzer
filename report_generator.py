import matplotlib
matplotlib.use('Agg')  # Usa il backend 'Agg' per generare grafici senza interfaccia grafica (utile per server/headless)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib.pyplot as plt
from datetime import datetime
import os
import numpy as np

# Salva un grafico matplotlib come immagine PNG
def save_chart(data, title, filename, chart_type='bar'):
    """
    Genera e salva un grafico (bar o pie) a partire dai dati forniti.
    Args:
        data (dict): Dati da visualizzare.
        title (str): Titolo del grafico.
        filename (str): Percorso dove salvare il file PNG.
        chart_type (str): Tipo di grafico ('bar' o 'pie').
    """
    if not data: # Non tentare di generare un grafico se non ci sono dati
        print(f"ℹ️ Nessun dato fornito per il grafico: {title}")
        return

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))

    keys = [str(k) for k in data.keys()] # Assicura che le chiavi siano stringhe per matplotlib
    values = list(data.values())

    if chart_type == 'bar':
        bars = ax.bar(keys, values, color=plt.cm.viridis(np.linspace(0.4, 0.8, len(keys))))
        ax.set_ylabel("Numero di Eventi/Tentativi")
        plt.xticks(rotation=45, ha="right") # Migliore rotazione e allineamento etichette asse x

        # Aggiungi i valori sopra le barre
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * max(values), # Leggero offset sopra la barra
                    f'{int(yval)}', # Mostra il valore intero
                    ha='center', va='bottom', fontsize=9)

    elif chart_type == 'pie' and sum(values) > 0: # Grafico a torta solo se ci sono valori > 0
        ax.pie(values, labels=keys, autopct='%1.1f%%', startangle=90,
               colors=plt.cm.viridis(np.linspace(0, 1, len(keys))))
        ax.axis('equal') # Assicura che la torta sia circolare

    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.tight_layout() # Aggiusta il layout per evitare sovrapposizioni

    try:
        plt.savefig(filename)
        print(f"📈 Grafico salvato: {filename}")
    except Exception as e:
        print(f"❌ Errore durante il salvataggio del grafico {filename}: {e}")
    finally:
        plt.close(fig) # Chiudi la figura specifica per liberare memoria

# Crea il report PDF
def generate_report(summary, anomalies, filename):
    """
    Genera un report PDF con tabelle e grafici a partire dai dati di analisi.
    Args:
        summary (dict): Dati aggregati dell'analisi (ip_counter, hourly_counter).
        anomalies (list): Lista di IP anomali rilevati.
        filename (str): Percorso dove salvare il PDF.
    """
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    ip_counter = summary["ip_counter"]
    hourly_counter = summary["hourly_counter"]

    # Titolo e data del report
    elements.append(Paragraph("📄 Report Analisi Log di Sicurezza", styles["Title"]))
    elements.append(Paragraph(f"Generato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Spacer(1, 24)) # Spazio dopo il titolo

    # Sezione 1: IP sospetti (Top 5) - Tabella
    elements.append(Paragraph("1. Indirizzi IP con Maggiore Attività (Top 5)", styles["Heading2"]))
    if ip_counter:
        # Dati per la tabella, inclusa l'intestazione
        data_ip = [["Indirizzo IP", "Numero Tentativi/Eventi"]]
        for ip, count in ip_counter.most_common(5):
            data_ip.append([Paragraph(ip, styles["Normal"]), str(count)]) # Usiamo Paragraph per l'IP per coerenza di stile

        ip_table = Table(data_ip, colWidths=[3*inch, 2*inch]) # Specifica larghezza colonne
        ip_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")), # Blu scuro per intestazione
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#DCE6F1")), # Blu chiaro per righe dati
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(ip_table)
    else:
        elements.append(Paragraph("Nessuna attività IP registrata.", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Sezione 2: Distribuzione oraria - Tabella
    elements.append(Paragraph("2. Distribuzione Oraria dei Tentativi/Eventi", styles["Heading2"]))
    if hourly_counter:
        # Dati per la tabella, inclusa l'intestazione
        data_hourly = [["Fascia Oraria", "Numero Tentativi/Eventi"]]
        for hour, count in sorted(hourly_counter.items()):
            data_hourly.append([f"{hour:02d}:00 - {hour:02d}:59", str(count)])

        hourly_table = Table(data_hourly, colWidths=[2.5*inch, 2.5*inch]) # Specifica larghezza colonne
        hourly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#DCE6F1")),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(hourly_table)
    else:
        elements.append(Paragraph("Nessuna attività oraria registrata.", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Sezione 3: IP anomali - Tabella
    elements.append(Paragraph("3. Indirizzi IP Anomali Rilevati", styles["Heading2"]))
    if anomalies:
        # Mini-tabella per IP anomali
        data_anomalies = [["Indirizzo IP Anomalo", "Tentativi/Eventi Registrati"]]
        for ip in anomalies:
            count = ip_counter.get(ip, "N/D") # Prendiamo il conteggio da ip_counter, N/D se non presente
            data_anomalies.append([Paragraph(f"⚠️ {ip}", styles["Normal"]), str(count)])

        anomaly_table = Table(data_anomalies, colWidths=[3*inch, 2.5*inch])
        anomaly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#C00000")), # Rosso scuro per intestazione
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#FDEADA")), # Arancione chiaro per righe dati
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(anomaly_table)
    else:
        elements.append(Paragraph("Nessuna anomalia rilevata dal modello.", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Sezione 4: Grafici di riepilogo (salvati come immagini PNG e inseriti nel PDF)
    ip_chart_path = "output/ip_chart.png"
    hour_chart_path = "output/hour_chart.png"
    if not os.path.exists("output"):
        os.makedirs("output") # Creazione cartella se non esiste

    # Grafico Top 5 IP
    if ip_counter:
        save_chart(dict(ip_counter.most_common(5)), "Top 5 IP per Attività", ip_chart_path)
        elements.append(Paragraph("4. Grafici di Riepilogo", styles["Heading2"]))
        elements.append(Image(ip_chart_path, width=5*inch, height=3*inch))
        elements.append(Spacer(1, 12))
    else:
        elements.append(Paragraph("4. Grafici di Riepilogo", styles["Heading2"]))
        elements.append(Paragraph("Nessun dato IP disponibile per il grafico.", styles["Normal"]))
        elements.append(Spacer(1,12))

    # Grafico distribuzione oraria
    if hourly_counter:
        save_chart(hourly_counter, "Distribuzione Oraria dei Tentativi/Eventi", hour_chart_path)
        elements.append(Image(hour_chart_path, width=5*inch, height=3*inch))
        elements.append(Spacer(1,12))
    else:
        elements.append(Paragraph("Nessun dato orario disponibile per il grafico.", styles["Normal"]))
        elements.append(Spacer(1,12))

    # Genera il PDF
    try:
        doc.build(elements)
        print(f"📄 Report PDF generato con successo: {filename}")
    except Exception as e:
        print(f"❌ Errore durante la costruzione del PDF: {e}")