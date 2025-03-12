import sqlite3
import json
import time
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QTextEdit

DB_NAME = "sensor_data.db"
SERIAL_PORT = "COM3"  # Endre til riktig port
BAUD_RATE = 9600

class SensorApp(QWidget):
    """ Programvindu for å legge til sensorer og sende/motta data. """

    def __init__(self):
        super().__init__()
        self.setup_gui()
        self.db = sqlite3.connect(DB_NAME)  # Koble til databasen
        self.cursor = self.db.cursor()
        self.setup_database()  # Lag databasen hvis den ikke finnes

    def setupGui(self):
        """ Lager menyen med knapper og tekstbokser. """
        self.setWindowTitle("Sensor System")
        layout = QVBoxLayout()

        self.sensor_input = QLineEdit()
        self.sensor_input.setPlaceholderText("Sensor Type")
        layout.addWidget(self.sensor_input)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Plassering")
        layout.addWidget(self.location_input)

        self.save_button = QPushButton("Lagre Sensor")
        self.save_button.clicked.connect(self.save_sensor)
        layout.addWidget(self.save_button)

        self.send_button = QPushButton("Send Sensorinfo")
        self.send_button.clicked.connect(self.send_to_microcontroller)
        layout.addWidget(self.send_button)

        self.read_button = QPushButton("Start Måling")
        self.read_button.clicked.connect(self.read_sensor_data)
        layout.addWidget(self.read_button)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.setLayout(layout)

    def setupDatabase(self):
        """ Lager en tabell i databasen hvis den ikke finnes. """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                location TEXT NOT NULL,
                date_added TEXT NOT NULL
            )
        """)
        self.db.commit()

    def saveSensor(self):
        """ Lagrer sensorinfo i databasen. """
        sensorType = self.sensor_input.text()
        location = self.location_input.text()

        if not sensorType or not location:
            self.log("Feil: Fyll ut begge feltene!")
            return

        self.cursor.execute("""
            INSERT INTO sensors (type, location, date_added)
            VALUES (?, ?, ?)
        """, (sensorType, location, time.strftime("%Y-%m-%d")))
        self.db.commit()

        self.log(f"Lagret sensor: {sensor_type} på {location}")

    def sendToMicrocontroller(self):
        """ Sender sensorinfo til mikrokontrolleren. """
        config_data = {"SensorConfiguration": {}}

        self.cursor.execute("SELECT id, type FROM sensors")
        sensors = self.cursor.fetchall()

        for sensorId, sensorType in sensors:
            if "temp" in sensorType.lower():
                config_data["SensorConfiguration"]["TemperatureSensor"] = {"Type": sensorType, "SensorId": sensorId}
            elif "accel" in sensorType.lower():
                config_data["SensorConfiguration"]["Accelerometer"] = {"Type": sensorType, "SensorId": sensorId}

        if not config_data["SensorConfiguration"]:
            self.log("Ingen sensorer funnet!")
            return

        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                ser.write(json.dumps(config_data).encode())
                self.log(f"Sendte data:\n{json.dumps(config_data, indent=4)}")

        except serial.SerialException as e:
            self.log(f"Seriell feil: {e}")

    def readSensorData(self):
        """ Leser data fra mikrokontrolleren og lagrer det. """
        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                ser.write(json.dumps({"Command": "START"}).encode())
                self.log("Starter måling...")

                while True:
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        try:
                            data = json.loads(line)
                            self.store_data(data)
                        except json.JSONDecodeError:
                            self.log("Feil: Klarte ikke å lese data.")

        except serial.SerialException as e:
            self.log(f"Seriell feil: {e}")

    def storeData(self, data):
        """ Lagrer sensordata i databasen. """
        try:
            if "temperature" in data:
                self.cursor.execute("""
                    INSERT INTO temperature_readings (sensorId, temperature, timestamp)
                    VALUES (?, ?, ?)
                """, (data["temperature"]["Sensor_id"], data["temperature"]["temperature"], time.strftime("%Y-%m-%d %H:%M:%S")))
                self.db.commit()
                self.log(f"Lagret temperaturdata: {data}")

            if "acceleration" in data:
                self.cursor.execute("""
                    INSERT INTO acceleration_readings (sensorId, x, y, z, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (data["acceleration"]["Sensor_id"], data["acceleration"]["x"], data["acceleration"]["y"], data["acceleration"]["z"], time.strftime("%Y-%m-%d %H:%M:%S")))
                self.db.commit()
                self.log(f"Lagret akselerasjonsdata: {data}")

        except sqlite3.Error as e:
            self.log(f"Databasefeil: {e}")

    def log(self, message):
        """ Skriver meldinger i loggboksen. """
        self.log_box.append(message)


if __name__ == "__main__":
    app = QApplication([])
    gui = SensorApp()
    gui.show()
    app.exec_()
