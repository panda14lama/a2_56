import sqlite3
import json
import time
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QTextEdit
"""
Konfigrasjon til database
"""
DB_NAME = "Sensordata.db"
SERIAL_PORT = "COM3"  # Endre til riktig port for mikrokontrolleren (f.eks. "/dev/ttyUSB0" på Linux)
BAUD_RATE = 9600

"""
klasse for sensor gui
"""
class SensorGui(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.db_connection = sqlite3.connect(DB_NAME)
        self.db_cursor = self.db_connection.cursor()
        self.create_table()

    def initUI(self):
        self.setWindowTitle("Sensor Administrasjon")
        layout = QVBoxLayout()

        #  Input for sensorregistrering
        self.sensorTypeLabel = QLabel("Sensor Type:")
        self.sensorTypeInput = QLineEdit()
        layout.addWidget(self.sensorTypeLabel)
        layout.addWidget(self.sensorTypeInput)

        self.locationLabel = QLabel("Lokasjon:")
        self.locationInput = QLineEdit()
        layout.addWidget(self.locationLabel)
        layout.addWidget(self.locationInput)

        #  Knapp for å legge til sensor
        self.addButton = QPushButton("Legg til Sensor")
        self.addButton.clicked.connect(self.add_sensor)
        layout.addWidget(self.addButton)

        #  Knapp for å hente og sende konfigurasjon
        self.sendConfigButton = QPushButton("Send Konfigurasjon")
        self.sendConfigButton.clicked.connect(self.send_configuration)
        layout.addWidget(self.sendConfigButton)

        # Knapp for å starte sensorinnsamling
        self.startReadButton = QPushButton("Start Sensorinnsamling")
        self.startReadButton.clicked.connect(self.start_reading)
        layout.addWidget(self.startReadButton)

        #  Statusfelt
        self.status = QLabel("")
        layout.addWidget(self.status)

        #  Loggfelt
        self.logField = QTextEdit()
        self.logField.setReadOnly(True)
        layout.addWidget(self.logField)

        self.setLayout(layout)


    def createTable(self):
        """Sikrer at tabellen for sensorer finnes i databasen"""
        self.db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                location TEXT NOT NULL,
                installation_date TEXT NOT NULL
            )
        """)
        self.db_connection.commit()


    def addSensor(self):
        """Legger til en ny sensor i databasen"""
        sensor_type = self.sensorTypeInput.text()
        location = self.locationInput.text()

        if not sensor_type or not location:
            self.status.setText(" Feil: Sensor Type og Lokasjon må fylles ut!")
            return

        try:
            self.db_cursor.execute("""
                INSERT INTO sensors (type, location, installation_date) 
                VALUES (?, ?, ?)
            """, (sensor_type, location, time.strftime("%Y-%m-%d")))
            self.db_connection.commit()

            self.status.setText(f" Sensor '{sensor_type}' i '{location}' lagt til!")
        except sqlite3.Error as e:
            self.status.setText(f"️ Databasefeil: {e}")


    def sendConfiguration(self):
        """Henter sensorer fra databasen og sender konfigurasjonsdata til mikrokontrolleren"""
        config_data = {
            "command": "CONFIG",
            "sensors": []
        }

        try:
            self.db_cursor.execute("SELECT id, type, location FROM sensors")
            sensors = self.db_cursor.fetchall()

            for sensor in sensors:
                config_data["sensors"].append({
                    "id": sensor[0],
                    "type": sensor[1],
                    "location": sensor[2]
                })

            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                ser.write(json.dumps(config_data).encode())
                self.status.setText(" Konfigurasjon sendt til mikrokontrolleren!")
                self.log_message(f"🔧 Sendte data: {json.dumps(config_data, indent=4)}")

        except sqlite3.Error as e:
            self.status.setText(f" Databasefeil: {e}")
        except serial.SerialException as e:
            self.status.setText(f"️ Seriell feil: {e}")

    def startReading(self):
        """Starter datainnsamling fra mikrokontrolleren"""
        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                ser.write(json.dumps({"Command": "START"}).encode())
                self.status.setText("📡 Starter innsamling av sensordata...")

                while True:
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        try:
                            data = json.loads(line)
                            self.store_data(data)
                        except json.JSONDecodeError:
                            self.log_message(" Feil ved dekoding av JSON")

        except serial.SerialException as e:
            self.status.setText(f" Seriell feil: {e}")

    def storeData(self, data):
        """Lagrer mottatte sensordata i databasen"""
        try:
            if "temperature" in data:
                self.db_cursor.execute("""
                    INSERT INTO temperature_readings (sensorId, temperature, timestamp) 
                    VALUES (?, ?, ?)
                """, (data["temperature"]["sensorId"], data["temperature"]["temperature"], time.strftime("%Y-%m-%d %H:%M:%S")))
                self.db_connection.commit()
                self.log_message(f" Temperaturdata lagret: {data}")

            if "acceleration" in data:
                self.db_cursor.execute("""
                    INSERT INTO acceleration_readings (sensorId, x, y, z, timestamp) 
                    VALUES (?, ?, ?, ?, ?)
                """, (data["acceleration"]["sensorId"], data["acceleration"]["x"], data["acceleration"]["y"], data["acceleration"]["z"], time.strftime("%Y-%m-%d %H:%M:%S")))
                self.db_connection.commit()
                self.log_message(f" Akselerasjonsdata lagret: {data}")

        except sqlite3.Error as e:
            self.log_message(f" Databasefeil: {e}")

    def logMessage(self, message):
        """Legger til meldinger i loggfeltet"""
        self.logField.append(message)


"""
 OPPSTART AV PROGRAMMET 
"""
if __name__ == "__main__":
    app = QApplication([])
    gui = SensorGui()
    gui.show()
    app.exec_()

