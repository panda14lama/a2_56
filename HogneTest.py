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

        self.acceleration_x2 = 0
        self.acceleration_y2 = 0
        self.acceleration_z2 = 0

    def sendCommand(self, command):
        command_json = json.dumps({"Command": command})
        self.ser.write(command_json.encode())
        print(f"Sent: {command_json}")

    def insertTemperatureData(self,sensor_id, temperature):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
        INSERT INTO temperaturereadings (sensor_id, timestamp, temperature)
        VALUES (%s, %s, %s)
        ''', (sensor_id, timestamp, temperature))

    def insertAccelerationData(self, sensor_id, acceleration_x, acceleration_y, acceleration_z, diff_acceleration_x, diff_acceleration_y, diff_acceleration_z):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        self.cursor.execute('''
        INSERT INTO accelerationreadings (sensor_id, timestamp, acceleration_x, acceleration_y, acceleration_z, diff_acceleration_x, diff_acceleration_y, diff_acceleration_z)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (sensor_id,timestamp, acceleration_x, acceleration_y, acceleration_z, diff_acceleration_x, diff_acceleration_y, diff_acceleration_z))


        self.conn.commit()
        print('temprature transfered')
    def processData(self, data):
        try:
            dataJson = json.loads(data)

            print(dataJson)
            if "acceleration" and "temperature" in dataJson:
                print("hAR DATA A OG T")

                temperature_stamp = dataJson['temperature']
                sensor_id_temp = temperature_stamp['sensor_id']
                temperature = temperature_stamp['temperature']

                acceleration = dataJson['acceleration']
                sensor_id_acc = acceleration['sensor_id']
                acceleration_x = acceleration['x']
                acceleration_y = acceleration['y']
                acceleration_z = acceleration['z']

                diff_acceleration_x = self.acceleration_x2 - acceleration_x
                diff_acceleration_y = self.acceleration_y2 - acceleration_y
                diff_acceleration_z = self.acceleration_z2 - acceleration_z

                self.acceleration_x2 = acceleration_x
                self.acceleration_y2 = acceleration_y
                self.acceleration_z2 = acceleration_z

                #self.insertTemperatureData(sensor_id_temp, temperature)
                #self.insertAccelerationData(sensor_id_acc,acceleration_x, acceleration_y, acceleration_z, diff_acceleration_x, diff_acceleration_y, diff_acceleration_z)

            elif "acceleration" in dataJson:
                print("aks")
                acceleration = dataJson['acceleration']
                sensor_id_acc = acceleration['sensor_id']
                acceleration_x = acceleration['x']
                acceleration_y = acceleration['y']
                acceleration_z = acceleration['z']

                diff_acceleration_x = self.acceleration_x2 - acceleration_x
                diff_acceleration_y = self.acceleration_y2 - acceleration_y
                diff_acceleration_z = self.acceleration_z2 - acceleration_z

                self.acceleration_x2 = acceleration_x
                self.acceleration_y2 = acceleration_y
                self.acceleration_z2 = acceleration_z
                print(acceleration_z, acceleration_x, acceleration_y)
                print(diff_acceleration_x, diff_acceleration_y, diff_acceleration_z)

                self.insertAccelerationData(sensor_id_acc,acceleration_x, acceleration_y, acceleration_z, diff_acceleration_x, diff_acceleration_y, diff_acceleration_z)



            elif "temperature" in dataJson:
                print("temp")
                temprature_stamp = dataJson['temperature']
                temperature = temprature_stamp['temperature']

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
collector.sendCommand("START")
collector.run()

#time.sleep(30)
#collector.send_command("STOP")


