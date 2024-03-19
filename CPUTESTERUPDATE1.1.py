import json
import os
import urllib.request
import tkinter as tk
from tkinter import ttk

def download_update(update_url, update_dir):
    # Herunterladen der Update-Datei
    try:
        with urllib.request.urlopen(update_url) as response:
            data = response.read().decode('utf-8')
            update_data = json.loads(data)
    except Exception as e:
        print("Fehler beim Herunterladen des Updates:", e)
        return

    # Überprüfen, ob die Update-Datei vorhanden ist
    if not os.path.exists(update_dir):
        os.makedirs(update_dir)

    # Speichern der Update-Datei
    update_path = os.path.join(update_dir, 'update.json')
    with open(update_path, 'w') as update_file:
        json.dump(update_data, update_file, indent=4)
    
    print("Update erfolgreich heruntergeladen:", update_path)

    # Anwendung des Updates auf die Benutzeroberfläche
    if 'changes' in update_data:
        for change in update_data['changes']:
            if 'type' in change and change['type'] == 'feature':
                update_ui()

def update_ui():
    # Ändern der Button-Anordnung entsprechend der Version 1.1
    start_button.grid(row=0, column=0)
    stop_button.grid(row=0, column=1)
    start_test_button.grid(row=0, column=2)
    duration_slider.grid(row=1, column=0, columnspan=3)

if __name__ == "__main__":
    # URL zur Update-Datei auf GitHub
    update_url = "https://raw.githubusercontent.com/RapChapter/CPUTESTER/main/update.json"

    # Pfad zum Installationsverzeichnis des CPUTESTER-Programms
    install_dir = os.path.dirname(os.path.abspath(__file__))
    update_dir = os.path.join(install_dir, "updates")

    # Erstellen der Tkinter-Oberfläche für die Buttons
    root = tk.Tk()
    root.title("Pi Berechner Update")
    root.geometry("300x100")

    start_button = ttk.Button(root, text="Start")
    stop_button = ttk.Button(root, text="Stop")
    start_test_button = ttk.Button(root, text="Start Test")
    duration_slider = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, label="Testdauer (Minuten)")

    download_update(update_url, update_dir)

    root.mainloop()
