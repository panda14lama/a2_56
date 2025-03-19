from time import sleep

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

    def sendCommand(self, command):
        command_json = json.dumps({"Command": command})
        self.ser.write(command_json.encode())
        print(f"Sent: {command_json}")

    def insertTempratureData(self,sensor_id, temperature):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
        INSERT INTO temperaturereadings (sensor_id, timestamp, temperature)
        VALUES (%s, %s, %s)
        ''', (sensor_id, timestamp, temperature))
        self.conn.commit()

    def processData(self, data):
        try:
            dataJson = json.loads(data)

            print(dataJson)
            if "acceleration" and "temperature" in dataJson:
                print("hAR DATA A OG T")
                temperature_stamp = dataJson['temperature']
                print(temperature_stamp)
                temperature = temperature_stamp['temperature']
                #sensor_id_temp

                acceleration = dataJson['acceleration']
                acceleration_x = acceleration['x']
                acceleration_y = acceleration['y']
                acceleration_z = acceleration['z']

                #self.insertTempratureData(self.sensor_id, temperature)

            elif "acceleration" in dataJson:
                print("aks")
                acceleration = dataJson['acceleration']
                acceleration_x = acceleration['x']
                acceleration_y = acceleration['y']
                acceleration_z = acceleration['z']

            elif "temperature" in dataJson:
                print("temp")
                temprature_stamp = dataJson['temperature']
                print(temprature_stamp)
                temprature = temprature_stamp['temperature']

            else:
                print("no valid data recived")

        except json.JSONDecodeError:
            print("Received invalid JSON")

    def run(self):
        print('run')
        try:
            while True:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode().strip()

                    print(f"Received: {data}")
                    self.processData(data)
                    # Example: Insert dummy sensor data

                print('sleep')
                time.sleep(self.interval)
                print('sleep over')
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
    'database': 'sensordata'
}

# Set the frequency of the sensor in Hz
frequency = 1  # For example, 10 Hz

collector = SensorDataCollector(port='COM5', baudrate=9600, db_config=db_config, frequency=frequency)
#collector.send_command("START")
collector.run()

#time.sleep(30)
#collector.send_command("STOP")


