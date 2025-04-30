import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import sys

processes = {}

def run_script(command, text_widget, name, btn_start, btn_stop):
    print(f"[DEBUG] Lancement de : {command}")
    try:
        btn_start.config(state="disabled", background="grey")
        btn_stop.config(state="normal", background="red")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        processes[name] = process
        for line in process.stdout:
            text_widget.insert(tk.END, line)
            text_widget.see(tk.END)
        process.stdout.close()
        process.wait()

        btn_start.config(state="normal", background="green")
        btn_stop.config(state="disabled", background="grey")
    except Exception as e:
        text_widget.insert(tk.END, f"[ERREUR] Impossible de lancer {command}: {e}\n")

def stop_process(name, text_widget, btn_start, btn_stop):
    process = processes.get(name)
    if process and process.poll() is None:
        process.terminate()
        text_widget.insert(tk.END, f"\n[🛑] Processus '{name}' arrêté.\n")
        text_widget.see(tk.END)
    else:
        text_widget.insert(tk.END, f"\n[!] Processus '{name}' déjà arrêté ou inexistant.\n")

    btn_start.config(state="normal", background="green")
    btn_stop.config(state="disabled", background="grey")

def stop_all_processes():
    for name, process in processes.items():
        if process and process.poll() is None:
            process.terminate()
    for role in button_refs:
        btn_start, btn_stop, text_widget = button_refs[role]
        btn_start.config(state="normal", background="green")
        btn_stop.config(state="disabled", background="grey")
        text_widget.insert(tk.END, f"\n[🛑] Arrêt forcé de '{role}'.\n")
        text_widget.see(tk.END)

root = tk.Tk()
root.title("Interface RabbitMQ - Client / Workers / Résultats")

# Adapter la taille à l'écran
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.resizable(True, True)

frame_top = ttk.LabelFrame(root, text="Contrôles", padding=10)
frame_top.pack(fill="x", padx=10, pady=5)

frame_middle = ttk.LabelFrame(root, text="Logs", padding=10)
frame_middle.pack(fill="both", expand=True, padx=10, pady=5)

def create_scrolled_text(label, parent):
    frame = tk.Frame(parent)
    frame.pack(side="left", fill="both", expand=True, padx=5)
    tk.Label(frame, text=label).pack()
    txt = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=8, width=20)
    txt.pack(fill="both", expand=True)
    return txt

log_frame_top = tk.Frame(frame_middle)
log_frame_top.pack(fill="x", padx=5, pady=5)

log_frame_bottom = tk.Frame(frame_middle)
log_frame_bottom.pack(fill="both", expand=True, padx=5, pady=5)

text_client = create_scrolled_text("🟡 Requêtes envoyées (client_send.py)", log_frame_top)
text_result = create_scrolled_text("🟢 Résultats reçus (client_receive.py)", log_frame_top)

text_workers = {
    "add": create_scrolled_text("🔵 Worker ADD", log_frame_bottom),
    "sub": create_scrolled_text("🟣 Worker SUB", log_frame_bottom),
    "mul": create_scrolled_text("🟠 Worker MUL", log_frame_bottom),
    "div": create_scrolled_text("🔴 Worker DIV", log_frame_bottom)
}

button_refs = {}

def create_role_buttons(name, command, text_widget):
    btn_start = tk.Button(frame_top, text=f"▶️ {name}", bg="green")
    btn_stop = tk.Button(frame_top, text=f"🛑 Stop {name}", bg="grey", state="disabled")

    btn_start.config(command=lambda: threading.Thread(
        target=run_script,
        args=(command, text_widget, name.lower(), btn_start, btn_stop),
        daemon=True).start())

    btn_stop.config(command=lambda: stop_process(name.lower(), text_widget, btn_start, btn_stop))

    btn_start.pack(side="left", padx=2)
    btn_stop.pack(side="left", padx=2)

    button_refs[name.lower()] = (btn_start, btn_stop, text_widget)

# Boutons pour client, résultat, et les 4 workers
create_role_buttons("Client", [sys.executable, "client_send.py"], text_client)
create_role_buttons("Result", [sys.executable, "client_receive.py"], text_result)

for op in ["add", "sub", "mul", "div"]:
    create_role_buttons(f"Worker_{op}", [sys.executable, "worker.py", op], text_workers[op])

# Bouton global "STOP TOUS"
tk.Button(frame_top, text="🛑 Arrêter TOUS", bg="red", fg="white", font=("Arial", 10, "bold"),
          command=stop_all_processes).pack(side="right", padx=5)

root.mainloop()
