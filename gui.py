# gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk # Aggiunto ttk per widget stilizzati
import os
from datetime import datetime
import threading

# Importa le funzioni di analisi dal tuo progetto
from log_parser import parse_log
from analyzer import analyze_events
from model import detect_anomalies
from report_generator import generate_report
from database import init_db, save_anomalies, save_analysis_history, get_analysis_history
from utils import reset_all

# Definizione della palette colori e dei font per la GUI
COLOR_PRIMARY = "#2C3E50"      # Blu scuro
COLOR_SECONDARY = "#3498DB"    # Blu brillante
COLOR_ACCENT = "#2980B9"       # Blu per hover/click
COLOR_BACKGROUND = "#ECF0F1"   # Grigio molto chiaro
COLOR_TEXT_LIGHT = "#FFFFFF"   # Testo bianco
COLOR_TEXT_DARK = "#34495E"    # Testo grigio scuro
COLOR_SUCCESS = "#2ECC71"      # Verde
COLOR_WARNING = "#F39C12"      # Arancione
COLOR_ERROR = "#E74C3C"        # Rosso
FONT_PRIMARY = ("Helvetica", 10)
FONT_PRIMARY_BOLD = ("Helvetica", 10, "bold")
FONT_TITLE = ("Helvetica", 12, "bold")

class SecurityLogAnalyzerGUI:
    """
    Classe principale per la GUI dell'analizzatore di log di sicurezza.
    Gestisce la selezione file, lancia l'analisi, mostra lo storico e permette il reset del sistema.
    """
    def __init__(self, master):
        self.master = master
        master.title("Analizzatore Log di Sicurezza Avanzato")
        master.geometry("850x750") # Imposta la dimensione della finestra
        master.configure(bg=COLOR_BACKGROUND) # Sfondo della finestra principale

        # Stile per i widget ttk (per progressbar o treeview futuri)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background=COLOR_BACKGROUND, foreground=COLOR_TEXT_DARK, font=FONT_PRIMARY)
        style.configure("TButton", background=COLOR_SECONDARY, foreground=COLOR_TEXT_LIGHT, font=FONT_PRIMARY_BOLD, padding=6)
        style.map("TButton",
                  background=[('active', COLOR_ACCENT)],
                  foreground=[('active', COLOR_TEXT_LIGHT)])
        style.configure("TEntry", fieldbackground=COLOR_TEXT_LIGHT, foreground=COLOR_TEXT_DARK, font=FONT_PRIMARY)
        style.configure("TLabelframe", background=COLOR_BACKGROUND, bordercolor=COLOR_PRIMARY, font=FONT_TITLE)
        style.configure("TLabelframe.Label", foreground=COLOR_PRIMARY, background=COLOR_BACKGROUND, font=FONT_TITLE)

        init_db() # Inizializza il database all'avvio

        self.log_filepath = tk.StringVar() # Percorso del file log selezionato
        self.output_dir = "output"

        # Crea la cartella output se non esiste
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Frame principale
        main_frame = tk.Frame(master, padx=15, pady=15, bg=COLOR_BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Sezione selezione file log ---
        file_frame = tk.LabelFrame(main_frame, text=" 📂 Selezione File Log ", padx=15, pady=10,
                                   bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY, font=FONT_TITLE,
                                   relief=tk.GROOVE, bd=2)
        file_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(file_frame, text="Percorso File:", bg=COLOR_BACKGROUND, fg=COLOR_TEXT_DARK, font=FONT_PRIMARY).pack(side=tk.LEFT, padx=(0,5))
        self.log_entry = tk.Entry(file_frame, textvariable=self.log_filepath, width=60, state='readonly',
                                  font=FONT_PRIMARY, bg="#FFFFFF", fg=COLOR_TEXT_DARK, relief=tk.SOLID, bd=1)
        self.log_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True, ipady=4)
        
        self.browse_button = tk.Button(file_frame, text="Sfoglia...", command=self.browse_log_file,
                                       bg=COLOR_SECONDARY, fg=COLOR_TEXT_LIGHT, font=FONT_PRIMARY_BOLD,
                                       relief=tk.FLAT, padx=10, pady=5, activebackground=COLOR_ACCENT, activeforeground=COLOR_TEXT_LIGHT)
        self.browse_button.pack(side=tk.LEFT, padx=(5,0))

        # --- Pulsanti azione ---
        action_frame = tk.Frame(main_frame, pady=10, bg=COLOR_BACKGROUND)
        action_frame.pack(fill=tk.X)

        button_config = {
            "font": FONT_PRIMARY_BOLD,
            "fg": COLOR_TEXT_LIGHT,
            "relief": tk.RAISED,
            "padx": 15,
            "pady": 8,
            "activeforeground": COLOR_TEXT_LIGHT,
            "borderwidth": 0,
            "cursor": "hand2"
        }

        self.analyze_button = tk.Button(action_frame, text="🚀 Avvia Analisi", command=self.start_analysis_thread,
                                        bg=COLOR_SUCCESS, activebackground="#27AE60", **button_config)
        self.analyze_button.pack(side=tk.LEFT, expand=True, padx=5)

        self.history_button = tk.Button(action_frame, text="📜 Storico Analisi", command=self.show_history,
                                        bg=COLOR_SECONDARY, activebackground=COLOR_ACCENT, **button_config)
        self.history_button.pack(side=tk.LEFT, expand=True, padx=5)

        self.reset_button = tk.Button(action_frame, text="🔥 Resetta Tutto", command=self.confirm_reset,
                                      bg=COLOR_ERROR, activebackground="#C0392B", **button_config)
        self.reset_button.pack(side=tk.LEFT, expand=True, padx=5)

        # --- Area di output ---
        output_frame = tk.LabelFrame(main_frame, text=" Log Operazioni ", padx=15, pady=10,
                                     bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY, font=FONT_TITLE,
                                     relief=tk.GROOVE, bd=2)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=20, state='disabled',
                                                     bg="#FFFFFF", fg=COLOR_TEXT_DARK, font=("Consolas", 9),
                                                     relief=tk.SOLID, bd=1)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.print_output("Benvenuto nell'Analizzatore Log di Sicurezza Avanzato.\nSeleziona un file di log per iniziare l'analisi.")

    def print_output(self, message):
        """
        Stampa un messaggio nell'area di output della GUI con timestamp.
        """
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def _thread_safe_print_output(self, message):
        """
        Permette di stampare in modo sicuro da thread diversi.
        """
        self.master.after(0, self.print_output, message)

    def browse_log_file(self):
        """
        Apre una finestra di dialogo per selezionare un file di log.
        """
        filepath = filedialog.askopenfilename(
            title="Seleziona un file di log",
            filetypes=[("Log files", "*.log"), ("Tutti i files", "*.*")]
        )
        if filepath:
            self.log_filepath.set(filepath)
            self.print_output(f"File selezionato: {filepath}")

    def start_analysis_thread(self):
        """
        Avvia l'analisi in un thread separato per non bloccare la GUI.
        """
        if not self.log_filepath.get():
            messagebox.showwarning("Attenzione", "Per favore, seleziona prima un file di log.", icon='warning')
            return

        self._thread_safe_print_output("Avvio analisi in corso...")
        
        # Disabilita i pulsanti durante l'analisi
        self.browse_button.config(state='disabled')
        self.analyze_button.config(state='disabled')
        self.history_button.config(state='disabled')
        self.reset_button.config(state='disabled')
        
        analysis_thread = threading.Thread(target=self._run_analysis, daemon=True)
        analysis_thread.start()

    def _on_analysis_complete(self, success, message_for_user, pdf_filepath=None):
        """
        Callback chiamata al termine dell'analisi per riabilitare i pulsanti e mostrare un messaggio.
        """
        self.browse_button.config(state='normal')
        self.analyze_button.config(state='normal')
        self.history_button.config(state='normal')
        self.reset_button.config(state='normal')

        if success:
            messagebox.showinfo("Analisi Completata", message_for_user, icon='info')
        else:
            messagebox.showerror("Errore Analisi", message_for_user, icon='error')

    def _run_analysis(self):
        """
        Esegue l'analisi del log, il rilevamento anomalie, la generazione del report e il salvataggio nel database.
        Tutto viene eseguito in un thread separato.
        """
        log_path = self.log_filepath.get()
        
        _status_success = False
        _status_message_for_user = ""
        _status_pdf_path = None

        try:
            self._thread_safe_print_output(f"Parsing del log: {log_path}...")
            entries = parse_log(log_path)
            if not entries:
                _status_message_for_user = "Nessuna voce di 'Failed password' trovata nel log."
                self._thread_safe_print_output(_status_message_for_user)
                _status_success = True
            else:
                pdf_filename = os.path.join(self.output_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                _status_pdf_path = pdf_filename

                self._thread_safe_print_output("Analisi eventi in corso...")
                summary = analyze_events(entries)

                self._thread_safe_print_output("Rilevamento anomalie con AI in corso...")
                anomalies = detect_anomalies(summary)
                self._thread_safe_print_output(f"Eventi anomali rilevati: {', '.join(anomalies) if anomalies else 'Nessuno'}")

                self._thread_safe_print_output(f"Generazione report PDF: {pdf_filename}...")
                generate_report(summary, anomalies or [], pdf_filename)
                self._thread_safe_print_output("Report PDF generato con successo!")

                self._thread_safe_print_output("Salvataggio anomalie nel database...")
                save_anomalies(anomalies, summary["ip_counter"])
                self._thread_safe_print_output("Anomalie salvate.")

                self._thread_safe_print_output("Salvataggio storico analisi nel database...")
                save_analysis_history(log_path, pdf_filename)
                self._thread_safe_print_output("Storico analisi salvato.")
                
                _status_message_for_user = f"Analisi completata con successo! Report salvato in: {_status_pdf_path}"
                _status_success = True

        except Exception as e:
            error_msg_for_log = f"ERRORE durante l'analisi: {e}"
            self._thread_safe_print_output(error_msg_for_log)
            _status_message_for_user = f"Si è verificato un errore durante l'analisi: {e}"
            _status_success = False
        finally:
            self.master.after(0, self._on_analysis_complete, _status_success, _status_message_for_user, _status_pdf_path)

    def show_history(self):
        """
        Mostra una finestra con lo storico delle analisi effettuate e i link ai PDF generati.
        """
        history_data = get_analysis_history()

        history_window = tk.Toplevel(self.master)
        history_window.title("📜 Storico Analisi")
        history_window.geometry("750x550")
        history_window.configure(bg=COLOR_BACKGROUND)
        history_window.transient(self.master) # La finestra dello storico rimane sopra la principale
        history_window.grab_set() # Blocca l'interazione con la finestra principale

        text_frame = tk.Frame(history_window, bg=COLOR_BACKGROUND, padx=10, pady=10)
        text_frame.pack(fill=tk.BOTH, expand=True)

        history_text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, state='disabled',
                                                       bg="#FFFFFF", fg=COLOR_TEXT_DARK, font=("Consolas", 9),
                                                       relief=tk.SOLID, bd=1)
        history_text_widget.pack(fill=tk.BOTH, expand=True)

        history_text_widget.config(state='normal')
        if not history_data:
            history_text_widget.insert(tk.END, "Nessuna analisi precedente trovata.")
        else:
            history_text_widget.insert(tk.END, "--- Storico delle Analisi Effettuate ---\n\n", ('title',))
            
            for entry in history_data:
                history_text_widget.insert(tk.END, f"ID Analisi: ", ('label',))
                history_text_widget.insert(tk.END, f"{entry['id']}\n", ('text',))
                history_text_widget.insert(tk.END, f"Data/Ora: ", ('label',))
                history_text_widget.insert(tk.END, f"{entry['analysis_datetime']}\n", ('text',))
                history_text_widget.insert(tk.END, f"File Log Input: ", ('label',))
                history_text_widget.insert(tk.END, f"{entry['log_filepath']}\n", ('text',))
                history_text_widget.insert(tk.END, f"File PDF Output: ", ('label',))
                history_text_widget.insert(tk.END, f"{entry['pdf_output_filepath']}\n", ('text',))
                
                # Bottone per aprire direttamente il PDF del report
                pdf_button = tk.Button(history_text_widget, text="🔗 Apri Report", 
                                        command=lambda path=entry['pdf_output_filepath']: self.open_pdf(path),
                                        bg=COLOR_SECONDARY, fg=COLOR_TEXT_LIGHT, font=("Helvetica", 8, "bold"), 
                                        relief=tk.FLAT, padx=5, pady=2, cursor="hand2",
                                        activebackground=COLOR_ACCENT, activeforeground=COLOR_TEXT_LIGHT)
                history_text_widget.window_create(tk.END, window=pdf_button)
                history_text_widget.insert(tk.END, "\n\n", ('spacer',))
        
        # Definisci i tag per lo stile (opzionale, migliora la leggibilità)
        history_text_widget.tag_configure('title', font=FONT_TITLE, foreground=COLOR_PRIMARY, spacing3=10)
        history_text_widget.tag_configure('label', font=FONT_PRIMARY_BOLD, foreground=COLOR_PRIMARY)
        history_text_widget.tag_configure('text', font=FONT_PRIMARY, foreground=COLOR_TEXT_DARK)
        history_text_widget.tag_configure('spacer', spacing1=5)

        history_text_widget.config(state='disabled')

    def open_pdf(self, filepath):
        """
        Apre il file PDF del report con il visualizzatore predefinito del sistema operativo.
        """
        if not os.path.exists(filepath):
            messagebox.showerror("Errore", f"Il file PDF non esiste: {filepath}", icon='error')
            return
        try:
            if os.name == 'nt':
                os.startfile(filepath) # Windows
            elif os.uname().sysname == 'Darwin':
                import subprocess
                subprocess.call(('open', filepath)) # macOS
            else:
                import subprocess
                subprocess.call(('xdg-open', filepath)) # Linux
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire il file PDF: {e}", icon='error')
            self._thread_safe_print_output(f"Errore nell'apertura del PDF: {e}")

    def confirm_reset(self):
        """
        Chiede conferma all'utente e, se accetta, resetta il sistema (database e report).
        """
        response = messagebox.askyesno(
            "Conferma Reset",
            "⚠️ Sei sicuro di voler resettare completamente il sistema?\n"
            "Questo eliminerà il database e tutti i report PDF generati.",
            icon='warning'
        )
        if response:
            self.print_output("Reset del sistema in corso...")
            reset_all()
            self.print_output("Sistema resettato con successo!")
            self.log_filepath.set("")
            self.print_output("Benvenuto nell'Analizzatore Log di Sicurezza Avanzato.\nSeleziona un file di log per iniziare l'analisi.")

if __name__ == "__main__":
    # Avvia la GUI se il file viene eseguito direttamente
    root = tk.Tk()
    app = SecurityLogAnalyzerGUI(root)
    root.mainloop()