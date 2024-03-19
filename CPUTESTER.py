import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import psutil

# Methode, die Pi berechnet
def calculate_pi():
    q, r, t, k, n, l = 1, 0, 1, 1, 3, 3
    while True:
        if 4 * q + r - t < n * t:
            yield n
            nr = 10 * (r - n * t)
            n = ((10 * (3 * q + r)) // t) - 10 * n
            q *= 10
            r = nr
        else:
            nr = (2 * q + r) * l
            nn = (q * (7 * k + 2) + r * l) // (t * l)
            q *= k
            t *= l
            l += 2
            k += 1
            n = nn
            r = nr

# Hintergrundprozess für die Pi-Berechnung
paused_time = 0  # Zuerst definieren
def update_pi():
    global running, paused_time  # Hier global deklarieren
    start_time = time.perf_counter() - paused_time
    for digit in pi_generator:
        if not running:
            break
        pi_digits.append(str(digit))
        pi_string = "3." + "".join(pi_digits[1:])
        elapsed_time = time.perf_counter() - start_time
        time_var.set(f"Laufzeit: {elapsed_time:.2f} Sekunden")
        text_area.config(state=tk.NORMAL)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.INSERT, pi_string)
        text_area.config(state=tk.DISABLED)
        counter_var.set(f"Berechnete Stellen: {len(pi_digits)}")
        
        # Berechne die CPU-Punktzahl
        cpu_score = calculate_cpu_score(pi_digits, elapsed_time)
        cpu_score_var.set(f"CPU Punktzahl: {cpu_score:.2f}")
        
        time.sleep(0.005)  # Verlangsamt die Anzeige

# Funktion zur Berechnung der CPU-Punktzahl
def calculate_cpu_score(pi_digits, elapsed_time):
    if elapsed_time == 0:
        return 0
    return len(pi_digits) / elapsed_time

# Kontinuierliche Aktualisierung der CPU-Auslastung und Notfallstopp
def update_cpu_usage():
    cpu_100_start = None  # Zeitpunkt, zu dem die CPU zuerst 100% erreicht hat
    while app_running:
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_usage_var.set(f"CPU Auslastung: {cpu_usage}%")
        if emergency_stop_enabled.get() and cpu_usage == 100.0:
            if cpu_100_start is None:
                cpu_100_start = time.time()
            elif time.time() - cpu_100_start >= 30:
                stop_calculating()
                print("Notfallstopp ausgelöst wegen hoher CPU-Auslastung.")
                cpu_100_start = None
        else:
            cpu_100_start = None

def start_calculating():
    global running
    if not running:
        running = True
        paused_time = 0  # Setze die pausierte Zeit zurück
        threading.Thread(target=update_pi, daemon=True).start()

def stop_calculating():
    global running
    running = False

def toggle_emergency_stop():
    # Diese Funktion wird aufgerufen, wenn der Notfall-Stopp-Button gedrückt wird.
    pass  # Die Logik wird bereits durch die update_cpu_usage Funktion gehandhabt

def on_closing():
    global app_running
    app_running = False
    stop_calculating()
    root.destroy()

def reset_program():
    global pi_digits, paused_time
    pi_digits = []
    paused_time = 0
    counter_var.set("Berechnete Stellen: 0")
    time_var.set("Laufzeit: 0.00 Sekunden")
    cpu_score_var.set("CPU Punktzahl: 0.00")

def stop_for_duration(duration):
    def inner():
        reset_program()
        start_calculating()
        time.sleep(duration * 60)
        stop_calculating()
    return inner

def start_test():
    duration = duration_slider.get()
    threading.Thread(target=stop_for_duration(duration), daemon=True).start()

# Initialisiere die benötigten Variablen
running = False
app_running = True
pi_digits = []
pi_generator = calculate_pi()

# Erstelle die GUI
root = tk.Tk()
root.title("Pi Berechner")
root.geometry("500x500")
root.configure(bg="#333")

text_area = scrolledtext.ScrolledText(root, font=("Courier", 10), height=10, width=50)
text_area.pack(pady=10)

counter_var = tk.StringVar()
counter_var.set("Berechnete Stellen: 0")
counter_label = ttk.Label(root, textvariable=counter_var, background="#333", foreground="white")
counter_label.pack()

time_var = tk.StringVar()
time_var.set("Laufzeit: 0.00 Sekunden")
time_label = ttk.Label(root, textvariable=time_var, background="#333", foreground="white")
time_label.pack()

cpu_usage_var = tk.StringVar()
cpu_usage_var.set("CPU Auslastung: 0%")
cpu_usage_label = ttk.Label(root, textvariable=cpu_usage_var, background="#333", foreground="white")
cpu_usage_label.pack()

cpu_score_var = tk.StringVar()
cpu_score_var.set("CPU Punktzahl: 0.00")
cpu_score_label = ttk.Label(root, textvariable=cpu_score_var, background="#333", foreground="white")
cpu_score_label.pack()

emergency_stop_enabled = tk.BooleanVar()
emergency_stop_enabled.set(True)  # Standardmäßig eingeschaltet
emergency_stop_checkbutton = ttk.Checkbutton(root, text="Notfall Stop", variable=emergency_stop_enabled, onvalue=True, offvalue=False)
emergency_stop_checkbutton.pack()

start_button = ttk.Button(root, text="Start", command=start_calculating)
start_button.pack(pady=5)

stop_button = ttk.Button(root, text="Stop", command=stop_calculating)
stop_button.pack(pady=5)

duration_slider = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, label="Testdauer (Minuten)")
duration_slider.pack(pady=10)

start_test_button = ttk.Button(root, text="Start Test", command=start_test)
start_test_button.pack(pady=5)

# Starte den Thread für die CPU-Auslastungsanzeige
threading.Thread(target=update_cpu_usage, daemon=True).start()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
