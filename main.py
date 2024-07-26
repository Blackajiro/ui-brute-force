import pyautogui
import time
import itertools
import string
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog

class BruteForcerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Brute Forcer - F11 to Toggle")
        self.is_running = False

        self.config = self.load_config('config.json')

        # UI Elements
        self.create_widgets()

        self.passwords_tried = []
        self.passwords_list = []  # Aggiunto per memorizzare la lista di password

        # Bind F11 to start/stop functionality
        self.root.bind("<F11>", self.toggle_start_stop)

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {
                "input_field": {"x": 300, "y": 400},
                "login_button": {"x": 350, "y": 500},
                "sleep_time": 1,
                "min_password_length": 1
            }

    def save_config(self, config_file):
        with open(config_file, 'w') as file:
            json.dump(self.config, file, indent=4)

    def create_widgets(self):
        # Frame for Input Field
        input_frame = ttk.LabelFrame(self.root, text="Input Field", padding=(10, 5))
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(input_frame, text="X:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.input_field_x = ttk.Entry(input_frame, width=10)
        self.input_field_x.grid(row=0, column=1, padx=5, pady=5)
        self.input_field_x.insert(0, self.config['input_field']['x'])

        ttk.Label(input_frame, text="Y:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.input_field_y = ttk.Entry(input_frame, width=10)
        self.input_field_y.grid(row=1, column=1, padx=5, pady=5)
        self.input_field_y.insert(0, self.config['input_field']['y'])

        self.set_input_button = ttk.Button(input_frame, text="Set with cursor", command=self.set_input_coordinates)
        self.set_input_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Frame for Login Button
        login_frame = ttk.LabelFrame(self.root, text="Login Button", padding=(10, 5))
        login_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Label(login_frame, text="X:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.login_button_x = ttk.Entry(login_frame, width=10)
        self.login_button_x.grid(row=0, column=1, padx=5, pady=5)
        self.login_button_x.insert(0, self.config['login_button']['x'])

        ttk.Label(login_frame, text="Y:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.login_button_y = ttk.Entry(login_frame, width=10)
        self.login_button_y.grid(row=1, column=1, padx=5, pady=5)
        self.login_button_y.insert(0, self.config['login_button']['y'])

        self.set_login_button = ttk.Button(login_frame, text="Set with cursor", command=self.set_login_coordinates)
        self.set_login_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Frame for Sleep Time and Buttons
        control_frame = ttk.Frame(self.root, padding=(10, 5))
        control_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Min Password Length field
        ttk.Label(control_frame, text="Min Password Length:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.min_password_length = ttk.Entry(control_frame, width=10)
        self.min_password_length.grid(row=0, column=1, padx=5, pady=5)
        self.min_password_length.insert(0, self.config['min_password_length'])

        # Sleep time field
        ttk.Label(control_frame, text="Sleep Time (seconds):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.sleep_time = ttk.Entry(control_frame, width=10)
        self.sleep_time.grid(row=0, column=3, padx=5, pady=5)
        self.sleep_time.insert(0, self.config['sleep_time'])

        # Buttons
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start)
        self.start_button.grid(row=1, column=0, padx=5, pady=10)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop, state='disabled')
        self.stop_button.grid(row=1, column=1, padx=5, pady=10)

        # Load Password File button
        file_frame = ttk.Frame(self.root, padding=(10, 5))
        file_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.load_file_button = ttk.Button(file_frame, text="Load passwords from file", command=self.load_password_file)
        self.load_file_button.grid(row=2, column=0, padx=5, pady=10)

        # Passwords tried listbox
        ttk.Label(self.root, text="Passwords Tried:").grid(row=3, column=0, columnspan=2, padx=10, pady=5)
        self.passwords_listbox = tk.Listbox(self.root, width=80, height=10)
        self.passwords_listbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Configure column and row weights
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(3, weight=1)

    def update_config(self):
        self.config['input_field']['x'] = int(self.input_field_x.get())
        self.config['input_field']['y'] = int(self.input_field_y.get())
        self.config['login_button']['x'] = int(self.login_button_x.get())
        self.config['login_button']['y'] = int(self.login_button_y.get())
        self.config['sleep_time'] = float(self.sleep_time.get())
        self.config['min_password_length'] = int(self.min_password_length.get())
        self.save_config('config.json')

    def start(self):
        self.update_config()
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.thread = threading.Thread(target=self.run_brute_force)
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def run_brute_force(self):
        if self.passwords_list:
            self.run_with_loaded_passwords()
        else:
            self.run_with_generated_passwords()

    def run_with_loaded_passwords(self):
        for password in self.passwords_list:
            if not self.is_running:
                return
            self.try_password(password)

    def run_with_generated_passwords(self):
        charset = string.ascii_letters + string.digits
        min_length = self.config['min_password_length']
        max_length = 20  # Adjust as needed

        for length in range(min_length, max_length + 1):
            for password in itertools.product(charset, repeat=length):
                if not self.is_running:
                    return
                self.try_password(''.join(password))

    def try_password(self, password):
        print('Testing ' + password)

        # Clicca sul campo di input per selezionarlo
        pyautogui.click(self.config['input_field']['x'], self.config['input_field']['y'])

        print('Emptying Field')

        # Cancella il testo esistente premendo Backspace
        last_password = self.passwords_tried[-1] if self.passwords_tried else None
        length = len(last_password) if last_password is not None else len(password)
        for _ in range(length):
            pyautogui.press('backspace')

        # Scrive la nuova password
        pyautogui.write(password)

        # Clicca sul pulsante di login
        pyautogui.moveTo(self.config['login_button']['x'], self.config['login_button']['y'])
        pyautogui.mouseDown()
        pyautogui.mouseUp()

        print('Waiting')

        # Attende il tempo specificato
        time.sleep(self.config['sleep_time'])

        # Aggiunge la password alla lista dei tentativi e la visualizza nella listbox
        self.passwords_tried.append(password)
        self.passwords_listbox.insert(tk.END, password)

    def set_input_coordinates(self):
        self.show_countdown("input_field")

    def set_login_coordinates(self):
        self.show_countdown("login_button")

    def show_countdown(self, field_name):
        countdown_window = tk.Toplevel(self.root)
        countdown_window.title("")
        countdown_window.geometry("300x100")

        countdown_label = tk.Label(countdown_window, text="Get ready...")
        countdown_label.pack(pady=20)

        countdown_time = 5
        for i in range(countdown_time, 0, -1):
            countdown_label.config(text=f"Selecting coordinates in {i} seconds")
            countdown_window.update()
            time.sleep(1)

        countdown_window.destroy()

        x, y = pyautogui.position()
        if field_name == 'input_field':
            self.input_field_x.delete(0, tk.END)
            self.input_field_x.insert(0, x)
            self.input_field_y.delete(0, tk.END)
            self.input_field_y.insert(0, y)
        else:
            self.login_button_x.delete(0, tk.END)
            self.login_button_x.insert(0, x)
            self.login_button_y.delete(0, tk.END)
            self.login_button_y.insert(0, y)

    def load_password_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        with open(file_path, 'r') as file:
            self.passwords_list = [line.strip() for line in file]

        print(f"Loaded {len(self.passwords_list)} passwords from {file_path}")

    def toggle_start_stop(self, event):
        if self.is_running:
            self.stop()
        else:
            self.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = BruteForcerApp(root)
    root.mainloop()
