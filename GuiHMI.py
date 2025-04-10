# Importerer nødvendige biblioteker for GUI, plotting og tidshåndtering
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from DbTrans import HentData  # Importerer klassen som henter sensorverdier fra databasen


# Hovedklassen som definerer GUI-en for sensorovervåking
class SensorGUI:
    def __init__(self, root, fetcher):
        self.root = root
        self.root.title("Sensorovervåking")  # Setter tittel på vinduet
        self.root.geometry("1400x700")       # Setter vindusstørrelse
        self.root.minsize(1400, 700)         # Minimumsstørrelse
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        # Lagrer sanntidsdata for plotting
        self.temperatures = []
        self.accelerations = []
        self.timestamps = []

        self.fetcher = fetcher  # Datainnhentingsobjekt, f.eks. fra database

        # Variabler for historisk visning
        self.history_start = tk.StringVar(value="00:00:00")
        self.history_end = tk.StringVar(value="23:59:59")
        self.view_mode = tk.StringVar(value="Live")  # Live eller historikk

        self.build_gui()   # Bygger grensesnittet
        self.update_gui()  # Starter oppdateringsloop


    def build_gui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Radioknapper for å velge visningsmodus
        mode_frame = tk.Frame(main_frame)
        mode_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Radiobutton(mode_frame, text="Live-visning", variable=self.view_mode, value="Live").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Historikk", variable=self.view_mode, value="History").pack(side=tk.LEFT)

        # Tidspunkt-felter for historikkmodus
        tk.Label(mode_frame, text="Fra (HH:MM:SS):").pack(side=tk.LEFT, padx=(20, 0))
        ttk.Entry(mode_frame, width=10, textvariable=self.history_start).pack(side=tk.LEFT)
        tk.Label(mode_frame, text="Til (HH:MM:SS):").pack(side=tk.LEFT)
        ttk.Entry(mode_frame, width=10, textvariable=self.history_end).pack(side=tk.LEFT)
        ttk.Button(mode_frame, text="Enter", command=self.plot_data).pack(side=tk.LEFT, padx=10)

        # Tekstetiketter for nåværende temperatur og akselerasjon
        self.temp_label = tk.Label(main_frame, text="Temperatur: -", font=("Arial", 14))
        self.temp_label.pack(fill=tk.X)
        self.accel_label = tk.Label(main_frame, text="Akselerasjon: -", font=("Arial", 14))
        self.accel_label.pack(fill=tk.X)

        # Lager figurer og akser for plotting
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 2), gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.5})
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(20, 40))

        # Viser alarmstatus med lys (grønn/rød)
        alarm_frame = tk.Frame(main_frame)
        alarm_frame.pack(side=tk.BOTTOM, anchor='se', padx=20, pady=10)
        tk.Label(alarm_frame, text="Alarmstatus (Temp):", font=("Arial", 14)).pack(side=tk.LEFT)
        self.green_light = tk.Canvas(alarm_frame, width=40, height=40)
        self.green_light.pack(side=tk.LEFT, padx=10)
        self.green_light_indicator = self.green_light.create_oval(5, 5, 35, 35, fill="gray")
        self.red_light = tk.Canvas(alarm_frame, width=40, height=40)
        self.red_light.pack(side=tk.LEFT, padx=10)
        self.red_light_indicator = self.red_light.create_oval(5, 5, 35, 35, fill="gray")

        tk.Label(alarm_frame, text=" Akselerasjon:", font=("Arial", 14)).pack(side=tk.LEFT)
        self.accel_green_light = tk.Canvas(alarm_frame, width=40, height=40)
        self.accel_green_light.pack(side=tk.LEFT, padx=10)
        self.accel_green_indicator = self.accel_green_light.create_oval(5, 5, 35, 35, fill="gray")
        self.accel_red_light = tk.Canvas(alarm_frame, width=40, height=40)
        self.accel_red_light.pack(side=tk.LEFT, padx=10)
        self.accel_red_indicator = self.accel_red_light.create_oval(5, 5, 35, 35, fill="gray")

        # Loggboks for hendelser
        log_frame = tk.Frame(self.root)
        log_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        tk.Label(log_frame, text="Hendelseslogg", font=("Arial", 12)).pack()
        self.log_box = tk.Listbox(log_frame, width=53, height=30)
        self.log_box.pack(fill=tk.BOTH, expand=True)
        ttk.Button(log_frame, text="Tøm logg", command=lambda: self.log_box.delete(0, tk.END)).pack(pady=5)

    def log_event(self, event):
        self.log_box.insert(tk.END, event)     # Legger til melding i loggboksen
        self.log_box.yview_moveto(1)           # Ruller automatisk til bunnen

    def update_gui(self):
        data = self.fetcher.return_data()      # Henter nyeste data
        if not data:
            self.root.after(1000, self.update_gui)  # Prøver igjen etter 1 sekund
            return

        # Trekker ut verdier
        temperature = data['temperature']
        x = data['x']
        y = data['y']
        z = data['z']
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Legger data til historikk
        self.timestamps.append(timestamp)
        self.temperatures.append(temperature)
        self.accelerations.append((x, y, z))

        # Hvis vi er i Live-modus: vis tall og alarmer
        if self.view_mode.get() == "Live":
            self.temp_label.config(text=f"Temperatur: {temperature} °C")
            self.accel_label.config(text=f"Akselerasjon: x={x}, y={y}, z={z}")

            # Temperatur-alarm
            if -4 <= temperature <= 28:
                self.green_light.itemconfig(self.green_light_indicator, fill="green")
                self.red_light.itemconfig(self.red_light_indicator, fill="gray")
            else:
                self.green_light.itemconfig(self.green_light_indicator, fill="gray")
                self.red_light.itemconfig(self.red_light_indicator, fill="red")
                self.log_event(f"[{timestamp}] Temperaturalarm: {temperature} °C")

            # Akselerasjons-alarm
            accel_threshold = 15
            if any(abs(axis) > accel_threshold for axis in [x, y, z]):
                self.accel_green_light.itemconfig(self.accel_green_indicator, fill="gray")
                self.accel_red_light.itemconfig(self.accel_red_indicator, fill="red")
                self.log_event(f"[{timestamp}] Akselerasjonsalarm: x={x}, y={y}, z={z}")
            else:
                self.accel_green_light.itemconfig(self.accel_green_indicator, fill="green")
                self.accel_red_light.itemconfig(self.accel_red_indicator, fill="gray")

            self.plot_data()  # Tegn grafen

        # Kjør denne funksjonen igjen etter 1 sekund
        self.root.after(1000, self.update_gui)

    def plot_data(self):
        self.ax1.clear()
        self.ax2.clear()

        if self.view_mode.get() == "History":
            # Filtrerer data mellom valgt tidspunkt
            start = self.history_start.get()
            end = self.history_end.get()
            try:
                filtered = [(t, temp, acc) for t, temp, acc in zip(self.timestamps, self.temperatures, self.accelerations)
                            if start <= t <= end]
                if not filtered:
                    raise ValueError
                time_data, temp_data, acc_data = zip(*filtered)
            except ValueError:
                messagebox.showwarning("Feil i tidsvalg", "Fant ikke data i valgt tidsintervall.")
                return
        else:
            # Henter siste 24 datapunkter for live-visning
            temp_data = self.temperatures[-24:]
            acc_data = self.accelerations[-24:]
            time_data = self.timestamps[-24:]

        # Plotter temperatur
        self.ax1.plot(time_data, temp_data, marker='o', label='Temperatur')
        self.ax1.axhline(y=0, color='gray', linestyle='--')
        self.ax1.axhline(y=-4, color='red', linestyle='--', label='-4°C')
        self.ax1.axhline(y=28, color='blue', linestyle='--', label='28°C')
        self.ax1.set_title("Temperatur")
        self.ax1.set_ylabel("°C")
        self.ax1.set_ylim(-20, 40)
        self.ax1.set_xticks(range(len(time_data)))
        self.ax1.set_xticklabels(time_data, rotation=45, ha='right')
        self.ax1.legend()

        # Plotter akselerasjon (x, y, z)
        self.ax2.plot(time_data, [a[0] for a in acc_data], label='x', color="red")
        self.ax2.plot(time_data, [a[1] for a in acc_data], label='y', color="green")
        self.ax2.plot(time_data, [a[2] for a in acc_data], label='z', color="blue")
        self.ax2.axhline(y=0, color='gray', linestyle='--')
        self.ax2.axhline(y=-15, color='red', linestyle='--', label='-15 m/s²')
        self.ax2.axhline(y=15, color='blue', linestyle='--', label='15 m/s²')
        self.ax2.set_title("Akselerasjon")
        self.ax2.set_ylabel("m/s²")
        self.ax2.set_ylim(-20, 20)
        self.ax2.set_xticks(range(len(time_data)))
        self.ax2.set_xticklabels(time_data, rotation=45, ha='right')
        self.ax2.legend()

        plt.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    dataHenter = HentData()  # Oppretter objekt for databasen
    app = SensorGUI(root, dataHenter)  # Starter GUI med databasen som kilde
    root.mainloop()  # Kjører GUI-løkken
