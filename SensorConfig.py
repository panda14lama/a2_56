import matplotlib.pyplot as plt
import json
import time
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit

"""
Lagring av sensor-data
"""
data_storage = {
    "sensors": [],
    "temperatureReadings": [],
    "accelerationReadings": []
}

"""
GUI for sensorregistrering
"""
class SensorGui(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Sensor Registrering")
        layout = QVBoxLayout()

        self.sensorTypeLabel = QLabel("Sensor Type:")
        self.sensorTypeInput = QLineEdit()
        layout.addWidget(self.sensorTypeLabel)
        layout.addWidget(self.sensorTypeInput)

        self.locationLabel = QLabel("Lokasjon:")
        self.locationInput = QLineEdit()
        layout.addWidget(self.locationLabel)
        layout.addWidget(self.locationInput)

        self.addButton = QPushButton("Legg til Sensor")
        self.addButton.clicked.connect(self.add_sensor)
        layout.addWidget(self.addButton)

        self.status = QLabel("")
        layout.addWidget(self.status)

        self.setLayout(layout)

    def add_sensor(self):
        sensorType = self.sensorTypeInput.text()
        location = self.locationInput.text()

        if not sensorType or not location:
            self.status.setText("Feil: Sensor Type og Lokasjon må fylles ut!")
            return

        sensorId = len(data_storage["sensors"]) + 1
        data_storage["sensors"].append({
            "sensorId": sensorId,
            "type": sensorType,
            "location": location,
            "installationDate": time.strftime("%Y-%m-%d")
        })

        self.status.setText(f"Sensor {sensorId} lagt til!")

"""
Datainnsamling
"""
class DataCollector:
    def __init__(self, port="COM3", baudrate=9600):
        try:
            self.serial_conn = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Feil ved åpning av seriell port: {e}")
            self.serial_conn = None

    def start_reading(self):
        if not self.serial_conn:
            print("Ingen seriell tilkobling.")
            return

        self.serial_conn.write(json.dumps({"Command": "START"}).encode())
        while True:
            line = self.serial_conn.readline().decode("utf-8").strip()
            if line:
                try:
                    data = json.loads(line)
                    self.store_data(data)
                except json.JSONDecodeError:
                    print("Feil ved dekoding av JSON")

    def store_data(self, data):
        if "temperature" in data:
            data_storage["temperatureReadings"].append({
                "sensorId": data["temperature"]["sensorId"],
                "temperature": data["temperature"]["temperature"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        if "acceleration" in data:
            data_storage["accelerationReadings"].append({
                "sensorId": data["acceleration"]["sensorId"],
                "x": data["acceleration"]["x"],
                "y": data["acceleration"]["y"],
                "z": data["acceleration"]["z"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

"""
Oppstart av GUI
"""
if __name__ == "__main__":
    app = QApplication([])
    gui = SensorGui()
    gui.show()
    app.exec_()

