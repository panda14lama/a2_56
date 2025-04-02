import tkinter as tk
from tkinter import messagebox, scrolledtext
import mysql.connector
import time
from mysql.connector import Error

class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor System")

        tk.Label(root, text="Sensor Type:").pack()
        self.sensor_input = tk.Entry(root)
        self.sensor_input.pack()

        tk.Label(root, text="Plassering:").pack()
        self.location_input = tk.Entry(root)
        self.location_input.pack()

        self.save_button = tk.Button(root, text="Lagre Sensor", command=self.save_sensor)
        self.save_button.pack()

        self.log_box = scrolledtext.ScrolledText(root, state='normal', height=10)
        self.log_box.pack()

        # MySQL-tilkobling
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="rgtt4Lama",
                database="sensordata"
            )
            self.cursor = self.db.cursor()
            self.log("Koblet til MySQL-database.")
        except Error as e:
            self.log(f"Feil ved tilkobling til database: {e}")

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def save_sensor(self):
        sensor_type = self.sensor_input.get()
        location = self.location_input.get()

        if not sensor_type or not location:
            messagebox.showwarning("Feil", "Begge feltene må fylles ut.")
            return

        try:
            self.cursor.execute("""
                INSERT INTO SENSORS (type, location, installation_date)
                VALUES (%s, %s, %s)
            """, (sensor_type, location, time.strftime("%Y-%m-%d")))
            self.db.commit()
            self.log(f"Lagret sensor: {sensor_type} på {location}")
        except Error as e:
            self.log(f"Databasefeil: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.mainloop()