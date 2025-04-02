import tkinter as tk
from tkinter import messagebox, scrolledtext
import mysql.connector
import time
from mysql.connector import Error
import serial  # For mikrokontrollerkommunikasjon


class SensorApp:
    """
    GUI-program for registrering og konfigurasjon av sensorer.
    Funksjonalitet:
    - Lagrer sensordata i MySQL-database.
    - Logger hendelser i GUI.
    - Sender konfigurasjonsdata til mikrokontroller via seriellport.
    """

    def __init__(self, root):
        """
        Initialiserer GUI, kobler til database, og setter opp grensesnitt.

        :param root: Tkinter-hovedvindu
        """
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
            self.log("✅ Koblet til MySQL-database.")
        except Error as e:
            self.log(f"❌ Feil ved tilkobling til database: {e}")

    def log(self, message):
        """
        Logger meldinger til GUI-loggboksen.

        :param message: Tekststreng som skal vises i loggen.
        """
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def send_to_microcontroller(self, sensor_type, location):
        """
        Sender sensordata til mikrokontroller via seriell tilkobling (USB).

        :param sensor_type: Type sensor (f.eks. "temp", "akk")
        :param location: Fysisk plassering for sensor
        """
        try:
            # Tilpass COM-port og baudrate til mikrokontrolleren din!
            with serial.Serial('COM5', 9600, timeout=2) as ser:
                config_data = f"type={sensor_type};location={location};\n"
                ser.write(config_data.encode('utf-8'))
                self.log(f"📤 Sendt til mikrokontroller: {config_data.strip()}")
        except serial.SerialException as e:
            self.log(f"❌ Feil ved sending til mikrokontroller: {e}")

    def save_sensor(self):
        """
        Henter input fra GUI, lagrer ny sensor i databasen dersom den ikke finnes fra før,
        og sender konfigurasjonsdata til mikrokontroller.
        """
        sensor_type = self.sensor_input.get().strip()
        location = self.location_input.get().strip()

        if not sensor_type or not location:
            messagebox.showwarning("Feil", "Begge feltene må fylles ut.")
            return

        try:
            # Sjekk om sensoren finnes fra før
            self.cursor.execute("""
                SELECT sensor_id FROM SENSORS
                WHERE type = %s AND location = %s
            """, (sensor_type, location))
            result = self.cursor.fetchone()

            if result:
                self.log("⚠️ Sensor finnes allerede – ikke lagret på nytt.")
                return

            # Sett inn sensor
            self.cursor.execute("""
                INSERT INTO SENSORS (type, location, installation_date)
                VALUES (%s, %s, %s)
            """, (sensor_type, location, time.strftime("%Y-%m-%d")))
            self.db.commit()
            self.log(f"✅ Lagret sensor: {sensor_type} på {location}")

            # Send til mikrokontroller
            self.send_to_microcontroller(sensor_type, location)

        except Error as e:
            self.log(f"❌ Databasefeil: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.mainloop()
