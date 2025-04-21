import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from DbTrans import HentData
import mplcursors


class SensorGUI:
    """
    GUI-applikasjon for visning og overvåking av sanntids- og historiske sensorverdier.

    Viser temperatur- og akselerasjonsdata, håndterer alarmgrenser, plotter data og viser hendelseslogg.
    """

    def __init__(self, root, fetcher):
        """
        Initialiserer GUI-en med hovedvindu, oppsett av komponenter og start på dataoppdatering.

        Args:
            root (tk.Tk): Hovedvindu for GUI.
            fetcher (HentData): Objekt for henting av sanntidsdata og grenseverdier.
        """
        self.root = root
        self.root.title("Sensorovervåking")
        self.root.geometry("1400x700")
        self.root.minsize(1900, 1100)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.cursor1 = None
        self.cursor2 = None

        self.temperatures = []
        self.accelerations = []
        self.timestamps = []

        self.threshold_temp_max = 0
        self.threshold_temp_min = 0
        self.threshold_acc = 0

        self.fetcher = fetcher

        self.history_start = tk.StringVar(value="00:00:00")
        self.history_end = tk.StringVar(value="23:59:59")
        self.view_mode = tk.StringVar(value="Live")

        self.build_gui()
        self.update_gui()

    def build_gui(self):
        """
        Bygger og konfigurerer alle grafiske komponenter i brukergrensesnittet.
        Inkluderer knapper, grafer, tekstfelter, statusindikatorer og loggboks.
        """
        main_frame = tk.Frame(self.root)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        mode_frame = tk.Frame(main_frame)
        mode_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Radiobutton(mode_frame, text="Live-visning", variable=self.view_mode, value="Live").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Historikk", variable=self.view_mode, value="History").pack(side=tk.LEFT)
        tk.Label(mode_frame, text="Fra (HH:MM:SS):").pack(side=tk.LEFT, padx=(20, 0))
        ttk.Entry(mode_frame, width=10, textvariable=self.history_start).pack(side=tk.LEFT)
        tk.Label(mode_frame, text="Til (HH:MM:SS):").pack(side=tk.LEFT)
        ttk.Entry(mode_frame, width=10, textvariable=self.history_end).pack(side=tk.LEFT)
        ttk.Button(mode_frame, text="Enter", command=self.plot_data).pack(side=tk.LEFT, padx=10)

        self.temp_label = tk.Label(main_frame, text="Temperatur: -", font=("Arial", 14))
        self.temp_label.pack(fill=tk.X)
        self.accel_label = tk.Label(main_frame, text="Akselerasjon: -", font=("Arial", 14))
        self.accel_label.pack(fill=tk.X)

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 2), gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.5})
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(20, 40))

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

        log_frame = tk.Frame(self.root)
        log_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        tk.Label(log_frame, text="Hendelseslogg", font=("Arial", 12)).pack()
        self.log_box = tk.Listbox(log_frame, width=53, height=30)
        self.log_box.pack(fill=tk.BOTH, expand=True)
        ttk.Button(log_frame, text="Tøm logg", command=lambda: self.log_box.delete(0, tk.END)).pack(pady=5)

        temp_threshold = self.fetcher.hent_threshold_temp()
        acc_threshold = self.fetcher.hent_threshold_acc()
        self.threshold_temp_max = temp_threshold[0]['max_value']
        self.threshold_temp_min = temp_threshold[0]['min_value']
        self.threshold_acc = acc_threshold[0]['max_value']

    def log_event(self, event):
        """
        Legger en ny hendelse til i hendelsesloggen.

        Args:
            event (str): Meldingen som skal loggføres.
        """
        self.log_box.insert(tk.END, event)
        self.log_box.yview_moveto(1)

    def update_gui(self):
        """
        Henter ny sanntidsdata, oppdaterer visning og varsler om alarmer.
        Kalles periodisk hvert sekund for å oppdatere GUI og plot.
        """
        data = self.fetcher.return_data()
        if not data:
            self.root.after(1000, self.update_gui)
            return

        temperature = data['temperature']
        x = data['x']
        y = data['y']
        z = data['z']
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.timestamps.append(timestamp)
        self.temperatures.append(temperature)
        self.accelerations.append((x, y, z))

        if self.view_mode.get() == "Live":
            self.temp_label.config(text=f"Temperatur: {temperature} °C")
            self.accel_label.config(text=f"Akselerasjon: x={x}, y={y}, z={z}")

            if self.threshold_temp_min <= temperature <= self.threshold_temp_max:
                self.green_light.itemconfig(self.green_light_indicator, fill="green")
                self.red_light.itemconfig(self.red_light_indicator, fill="gray")
            else:
                self.green_light.itemconfig(self.green_light_indicator, fill="gray")
                self.red_light.itemconfig(self.red_light_indicator, fill="red")
                self.log_event(f"[{timestamp}] Temperaturalarm: {temperature} °C")

            if any(abs(axis) > self.threshold_acc for axis in [x, y, z]):
                self.accel_green_light.itemconfig(self.accel_green_indicator, fill="gray")
                self.accel_red_light.itemconfig(self.accel_red_indicator, fill="red")
                self.log_event(f"[{timestamp}] Akselerasjonsalarm: x={x}, y={y}, z={z}")
            else:
                self.accel_green_light.itemconfig(self.accel_green_indicator, fill="green")
                self.accel_red_light.itemconfig(self.accel_red_indicator, fill="gray")

            self.plot_data()

        self.root.after(1000, self.update_gui)

    def plot_data(self):
        """
        Plotter temperatur- og akselerasjonsdata i henhold til valgt visningsmodus (live/historikk).
        Viser også grenseverdier i grafene og aktiverer markør for interaksjon.
        """
        self.ax1.clear()
        self.ax2.clear()

        if self.cursor1:
            self.cursor1.remove()
            self.cursor1 = None
        if self.cursor2:
            self.cursor2.remove()
            self.cursor2 = None

        if self.view_mode.get() == "History":
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
            temp_data = self.temperatures[-24:]
            acc_data = self.accelerations[-24:]
            time_data = self.timestamps[-24:]

        self.ax1.plot(time_data, temp_data, marker='o', label='Temperatur')
        self.ax1.axhline(y=0, color='gray', linestyle='--')
        self.ax1.axhline(y=self.threshold_temp_min, color='red', linestyle='--', label=f'{self.threshold_temp_min}°C')
        self.ax1.axhline(y=self.threshold_temp_max, color='blue', linestyle='--', label=f'{self.threshold_temp_max}°C')
        self.ax1.set_title("Temperatur")
        self.ax1.set_ylabel("°C")
        self.ax1.set_ylim(-20, 40)
        self.ax1.set_xticks(range(len(time_data)))
        self.ax1.set_xticklabels(time_data, rotation=45, ha='right')
        self.ax1.legend()

        self.ax2.plot(time_data, [a[0] for a in acc_data], label='x', color="red")
        self.ax2.plot(time_data, [a[1] for a in acc_data], label='y', color="green")
        self.ax2.plot(time_data, [a[2] for a in acc_data], label='z', color="blue")
        self.ax2.axhline(y=0, color='gray', linestyle='--')
        self.ax2.axhline(y=-self.threshold_acc, color='red', linestyle='--', label=f'-{self.threshold_acc} m/s²')
        self.ax2.axhline(y=self.threshold_acc, color='blue', linestyle='--', label=f'{self.threshold_acc} m/s²')
        self.ax2.set_title("Akselerasjon")
        self.ax2.set_ylabel("m/s²")
        self.ax2.set_ylim(-20, 20)
        self.ax2.set_xticks(range(len(time_data)))
        self.ax2.set_xticklabels(time_data, rotation=45, ha='right')
        self.ax2.legend()

        plt.tight_layout()
        self.canvas.draw()
        self.cursor1 = mplcursors.cursor(self.ax1, hover=True)
        self.cursor2 = mplcursors.cursor(self.ax2, hover=True)
        plt.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    """
    Starter GUI-applikasjonen med tilkobling til datakilde.
    """
    root = tk.Tk()
    dataHenter = HentData()
    app = SensorGUI(root, dataHenter)
    root.mainloop()
