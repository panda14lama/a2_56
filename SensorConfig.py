
import serial
import json
import time
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QTextEdit

# Simulert lagring av sensorinformasjon
data_storage = {
    "sensors": [],
    "temperature_readings": [],
    "acceleration_readings": []
}


# GUI for Sensorregistrering
class SensorGUI(QWidget):
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
        sensor_type = self.sensorTypeInput.text()
        location = self.locationInput.text()

        sensor_id = len(data_storage["sensors"]) + 1
        data_storage["sensors"].append({
            "sensor_id": sensor_id,
            "type": sensor_type,
            "location": location,
            "installation_date": time.strftime("%Y-%m-%d")
        })

        self.status.setText(f"Sensor {sensor_id} lagt til!")


# Simulert datainnsamling
class DataCollector:
    def __init__(self, port="COM3", baudrate=9600):
        self.serial_conn = serial.Serial(port, baudrate, timeout=1)

    def start_reading(self):
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
            data_storage["temperature_readings"].append({
                "sensor_id": data["temperature"]["sensor_id"],
                "temperature": data["temperature"]["temperature"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        if "acceleration" in data:
            data_storage["acceleration_readings"].append({
                "sensor_id": data["acceleration"]["sensor_id"],
                "x": data["acceleration"]["x"],
                "y": data["acceleration"]["y"],
                "z": data["acceleration"]["z"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })


# Oppstart
if __name__ == "__main__":
    app = QApplication([])
    gui = SensorGUI()
    gui.show()
    app.exec_()