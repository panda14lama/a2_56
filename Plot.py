import tkinter as tk
from tkinter import ttk, messagebox
import serial
import json
import random
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# Hent grenseverdier fra MySQL

def hent_grenseverdier():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="sensordata"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM grenseverdier LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result if result else {"temp_min": -4, "temp_max": 28, "accel_threshold": 15}
    except Exception as e:
        messagebox.showerror("Databasefeil", str(e))
        return {"temp_min": -4, "temp_max": 28, "accel_threshold": 15}

# Simulert datainnhenting hvis mikrokontroller ikke er tilgjengelig
def fetch_dummy_data():
    return {
        "temperature": {"temperature": round(random.uniform(-20, 40), 2), "sensor_id": 1},
        "acceleration": {
            "x": round(random.uniform(-10, 10), 3),
            "y": round(random.uniform(-10, 10), 3),
            "z": round(random.uniform(-10, 10), 3),
            "sensor_id": 2
        }
    }


def fetch_data_from_microcontroller():
    try:
        ser = serial.Serial('COM3', 9600, timeout=1)
        ser.write(json.dumps({"Command": "RETURN_DATA"}).encode())
        response = ser.readline().decode().strip()
        ser.close()
        data = json.loads(response) if response else fetch_dummy_data()
        data['temperature']['temperature'] = max(-20, min(40, data['temperature']['temperature']))
        return data
    except Exception:
        return fetch_dummy_data()


def log_event(event):
    log_box.insert(tk.END, event)
    log_box.yview_moveto(1)


def update_gui():
    global grenseverdier
    if view_mode.get() == "Live":
        data = fetch_data_from_microcontroller()
        timestamp = datetime.now().strftime("%H:%M:%S")

        timestamps.append(timestamp)
        temperatures.append(data['temperature']['temperature'])
        accelerations.append((data['acceleration']['x'], data['acceleration']['y'], data['acceleration']['z']))

        temp_label.config(text=f"Temperatur: {data['temperature']['temperature']}°C")
        accel_label.config(
            text=f"Akselerasjon: x={data['acceleration']['x']}, y={data['acceleration']['y']}, z={data['acceleration']['z']}"
        )

        temperature = data['temperature']['temperature']
        if grenseverdier['temp_min'] <= temperature <= grenseverdier['temp_max']:
            green_light.itemconfig(green_light_indicator, fill="green")
            red_light.itemconfig(red_light_indicator, fill="gray")
        else:
            green_light.itemconfig(green_light_indicator, fill="gray")
            red_light.itemconfig(red_light_indicator, fill="red")
            log_event(f"[{timestamp}] Temperaturalarm: {temperature}°C")

        accel_threshold = grenseverdier['accel_threshold']
        if (abs(data['acceleration']['x']) > accel_threshold or
            abs(data['acceleration']['y']) > accel_threshold or
            abs(data['acceleration']['z']) > accel_threshold):
            accel_green_light.itemconfig(accel_green_indicator, fill="gray")
            accel_red_light.itemconfig(accel_red_indicator, fill="red")
            log_event(f"[{timestamp}] Akselerasjonsalarm: x={data['acceleration']['x']}, y={data['acceleration']['y']}, z={data['acceleration']['z']}")
        else:
            accel_green_light.itemconfig(accel_green_indicator, fill="green")
            accel_red_light.itemconfig(accel_red_indicator, fill="gray")

        plot_data()
    root.after(5000, update_gui)


def plot_data():
    ax1.clear()
    ax2.clear()

    if view_mode.get() == "Live":
        temp_data = temperatures[-24:]  # siste 2 minutter (24 x 5 sek)
        acc_data = accelerations[-24:]
        time_data = timestamps[-24:]
    else:
        try:
            start_time = history_start.get()
            end_time = history_end.get()
            start_index = next(i for i, t in enumerate(timestamps) if t >= start_time)
            end_index = next(i for i, t in enumerate(timestamps) if t >= end_time)
            temp_data = temperatures[start_index:end_index]
            acc_data = accelerations[start_index:end_index]
            time_data = timestamps[start_index:end_index]
        except Exception:
            messagebox.showerror("Feil", "Bruk formatet HH:MM:SS for å angi klokkeslett.")
            return

    ax1.plot(time_data, temp_data, marker='o', label='Temperatur')
    ax1.axhline(y=0, color='gray', linestyle='--')
    ax1.axhline(y=-4, color='red', linestyle='--', label='-4°C')
    ax1.axhline(y=28, color='blue', linestyle='--', label='28°C')
    ax1.set_title("Temperatur")
    ax1.set_ylabel("°C")
    ax1.set_ylim(-20, 40)
    ax1.set_xticks(range(len(time_data)))
    ax1.set_xticklabels(time_data, rotation=45, ha='right')
    ax1.legend()

    ax2.plot(time_data, [a[0] for a in acc_data], label='x', color="red")
    ax2.plot(time_data, [a[1] for a in acc_data], label='y', color="green")
    ax2.plot(time_data, [a[2] for a in acc_data], label='z', color="blue")
    ax2.axhline(y=0, color='gray', linestyle='--')
    ax2.axhline(y=-15, color='red', linestyle='--', label='-15 m/s²')
    ax2.axhline(y=15, color='blue', linestyle='--', label='15 m/s²')
    ax2.set_title("Akselerasjon")
    ax2.set_ylabel("m/s²")
    ax2.set_ylim(-20, 20)
    ax2.set_xticks(range(len(time_data)))
    ax2.set_xticklabels(time_data, rotation=45, ha='right')
    ax2.legend()

    plt.tight_layout()
    canvas.draw()


# GUI setup
grenseverdier = hent_grenseverdier()

root = tk.Tk()
root.title("Sensorovervåking")
root.geometry("1400x700")
root.minsize(1400, 700)
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1)

main_frame = tk.Frame(root)
main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Legg GUI-elementene i main_frame istedenfor root

view_mode = tk.StringVar(value="Live")
history_start = tk.StringVar(value="00:00:00")
history_end = tk.StringVar(value="23:59:59")

mode_frame = tk.Frame(main_frame)
mode_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

live_radio = ttk.Radiobutton(mode_frame, text="Live-visning", variable=view_mode, value="Live")
live_radio.pack(side=tk.LEFT, padx=10)

history_radio = ttk.Radiobutton(mode_frame, text="Historikk", variable=view_mode, value="History")
history_radio.pack(side=tk.LEFT)

history_label1 = tk.Label(mode_frame, text="Fra (HH:MM:SS):")
history_label1.pack(side=tk.LEFT, padx=(20, 0))
history_entry1 = ttk.Entry(mode_frame, width=10, textvariable=history_start)
history_entry1.pack(side=tk.LEFT)

history_label2 = tk.Label(mode_frame, text="Til (HH:MM:SS):")
history_label2.pack(side=tk.LEFT)
history_entry2 = ttk.Entry(mode_frame, width=10, textvariable=history_end)
history_entry2.pack(side=tk.LEFT)

apply_button = ttk.Button(mode_frame, text="Enter", command=plot_data)
apply_button.pack(side=tk.LEFT, padx=10)

start_button = ttk.Button(mode_frame, text="Start", command=update_gui)
start_button.pack(side=tk.RIGHT, padx=10)

temp_label = tk.Label(main_frame, text="Temperatur: -", font=("Arial", 14))
temp_label.pack(fill=tk.X)

accel_label = tk.Label(main_frame, text="Akselerasjon: -", font=("Arial", 14))
accel_label.pack(fill=tk.X)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 2), gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.5})
canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(20, 40))

alarm_frame = tk.Frame(main_frame)
alarm_frame.pack(side=tk.BOTTOM, anchor='se', padx=20, pady=10)

alarm_label = tk.Label(alarm_frame, text="Alarmstatus (Temp):", font=("Arial", 14))
alarm_label.pack(side=tk.LEFT)

green_light = tk.Canvas(alarm_frame, width=40, height=40)
green_light.pack(side=tk.LEFT, padx=10)
green_light_indicator = green_light.create_oval(5, 5, 35, 35, fill="gray")

red_light = tk.Canvas(alarm_frame, width=40, height=40)
red_light.pack(side=tk.LEFT, padx=10)
red_light_indicator = red_light.create_oval(5, 5, 35, 35, fill="gray")

accel_alarm_label = tk.Label(alarm_frame, text=" Akselerasjon:", font=("Arial", 14))
accel_alarm_label.pack(side=tk.LEFT)

accel_green_light = tk.Canvas(alarm_frame, width=40, height=40)
accel_green_light.pack(side=tk.LEFT, padx=10)
accel_green_indicator = accel_green_light.create_oval(5, 5, 35, 35, fill="gray")

accel_red_light = tk.Canvas(alarm_frame, width=40, height=40)
accel_red_light.pack(side=tk.LEFT, padx=10)
accel_red_indicator = accel_red_light.create_oval(5, 5, 35, 35, fill="gray")

# Loggboks for alarmer integrert til høyre i hovedvinduet
log_frame = tk.Frame(root)
log_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
log_label = tk.Label(log_frame, text="Hendelseslogg", font=("Arial", 12))
log_label.pack()
log_box = tk.Listbox(log_frame, width=50, height=30)
log_box.pack(fill=tk.BOTH, expand=True)

# Tøm-knapp for logg
clear_button = ttk.Button(log_frame, text="Tøm logg", command=lambda: log_box.delete(0, tk.END))
clear_button.pack(pady=5)

temperatures = []
accelerations = []
timestamps = []

temperatures = []
accelerations = []
timestamps = []

root.mainloop()
