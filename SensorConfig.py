import sqlite3
import json
import time
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QTextEdit

DB_NAME = "sensor_data.db"
SERIAL_PORT = "COM3"  # Endre til riktig port
BAUD_RATE = 9600

class SensorWindow(QWidget):
    """ Programvindu for å legge til sensorer og sende/motta data. """

    def __init__(self):
        super().__init__()
        self.setupGui()
        self.db = sqlite3.connect(DB_NAME)  # Koble til databasen
        self.cursor = self.db.cursor()      #hente resultater, manipulere database

    def setupGui(self):
        """ Lager menyen med knapper og tekstbokser. """
        self.setWindowTitle("Sensor System")
        layout = QVBoxLayout()

        self.sensorInput = QLineEdit()
        self.sensorInput.setPlaceholderText("Sensor Type")
        layout.addWidget(self.sensorInput)

        self.locationInput = QLineEdit()
        self.locationInput.setPlaceholderText("Plassering")
        layout.addWidget(self.locationInput)

        self.saveButton = QPushButton("Lagre Sensor")
        self.saveButton.clicked.connect(self.saveSensor)
        layout.addWidget(self.saveButton)

        self.readButton = QPushButton("Start Måling")
        self.readButton.clicked.connect(self.readSensorData)
        layout.addWidget(self.readButton)

        self.logBox = QTextEdit()
        self.logBox.setReadOnly(True)
        layout.addWidget(self.logBox)

        self.setLayout(layout)

    def saveSensor(self):
        """ Lagrer sensorinfo i databasen. """
        sensorType = self.sensorInput.text()
        location = self.locationInput.text()

        if not sensorType or not location:
            self.log("Error")
            return

        self.cursor.execute("""
            INSERT INTO sensors (type, location, date_added)
            VALUES (?, ?, ?)
        """, (sensorType, location, time.strftime("%Y-%m-%d")))
        self.db.commit()

        self.log(f"Lagret sensor: {sensorType} på {location}")

    def readSensorData(self):
        """ Leser data fra mikrokontrolleren og lagrer det. """
        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser: # åpner kobling til microkontrolleren
                ser.write(json.dumps({"Command": "START"}).encode()) # Gjør det leslig av microkontrolleren
                self.log("Starter måling...")

                while True:
                    line = ser.readline().decode("utf-8").strip() #Leser data fra microkontrolleren
                    if line:
                        try:
                            data = json.loads(line)
                            self.storeData(data) #gjør om til json og lagrer dataen
                        except json.JSONDecodeError:
                            self.log("Feil: Klarte ikke å lese data.") # feilmelding

        except serial.SerialException as e:
            self.log(f"Error: {e}") # feilmelding av kobling til microkontroller

    def storeData(self, data):
        """ Lagrer sensordata i databasen. """
        try:
            if "temperature" in data:
                self.cursor.execute("""
                    INSERT INTO temperatureReadings (sensorId, temperature, timestamp)
                    VALUES (?, ?, ?)
                """, (data["temperature"]["SensorId"], data["temperature"]["temperature"], time.strftime("%Y-%m-%d %H:%M:%S")))
                self.db.commit()
                self.log(f"Lagret temperatur data: {data}")

            if "acceleration" in data:
                self.cursor.execute("""
                    INSERT INTO accelerationReadings (sensorId, x, y, z, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (data["acceleration"]["SensorId"], data["acceleration"]["x"], data["acceleration"]["y"], data["acceleration"]["z"], time.strftime("%Y-%m-%d %H:%M:%S")))
                self.db.commit()
                self.log(f"Lagret akselerasjonsdata: {data}")

        except sqlite3.Error as e:
            self.log(f"Databasefeil: {e}")

    def log(self, message):
        """ Skriver meldinger i loggboksen. """
        self.logBox.append(message)


if __name__ == "__main__":
    app = QApplication([])
    gui = SensorWindow()
    gui.show()
    app.exec_()
