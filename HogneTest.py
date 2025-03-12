import pymysql
import serial
import json
import time



class SensorDataCollector:
    def __init__(self, port, baudrate, db_config, frequency):
        self.port = port
        self.baudrate = baudrate
        self.db_config = db_config
        self.interval = 1 / frequency
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for the connection to establish
        self.conn = pymysql.connect(**db_config)
        self.cursor = self.conn.cursor()

    def insert_sensor_data(self, sensor_type, sensor_id, value):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
        INSERT INTO sensor_data (timestamp, sensor_type, sensor_id, value)
        VALUES (%s, %s, %s, %s)
        ''', (timestamp, sensor_type, sensor_id, value))
        self.conn.commit()

    def process_data(self, data):
        try:
            data_json = json.loads(data)
            if "SensorConfiguration" in data_json:
                for sensor, details in data_json["SensorConfiguration"].items():
                    print(f"Configured {sensor}: Type={details['Type']}, ID={details['Sensor_id']}")
            elif "Command" in data_json:
                command = data_json["Command"]
                if command == "START":
                    print("Starting data collection...")
                elif command == "STOP":
                    print("Stopping data collection...")
        except json.JSONDecodeError:
            print("Received invalid JSON")

    def run(self):
        print('run')
        try:
            while True:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode().strip()
                    print(data)
                    print(f"Received: {data}")
                    self.process_data(data)
                    # Example: Insert dummy sensor data
                    self.insert_sensor_data("EksempelNavn1", "id-nummer", 23.5)
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("Program terminated")
        finally:
            self.ser.close()
            self.conn.close()

# Example usage
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'msd'
}

# Set the frequency of the sensor in Hz
frequency = 5  # For example, 10 Hz

collector = SensorDataCollector(port='COM5', baudrate=115200, db_config=db_config, frequency=frequency)
collector.run()


