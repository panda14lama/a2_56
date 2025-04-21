from time import sleep

import pymysql
import serial
import json
import time

import threading


class SensorDataCollector:
    """
    Klasse for å hente og behandle sanntidsdata fra temperatursensor og akselerometer via seriell port.
    Støtter innsetting av målinger og alarmer til MySQL-database.
    """

    def __init__(self, port, frequency):
        """
        Initialiserer objektet med seriell port, målefrekvens og databaseforbindelse.

        Args:
            port (str): COM-porten som sensoren er koblet til.
            frequency (int): Antall målinger per sekund.
        """
        self.port = port
        self.baudrate = 9600
        self.frequency = frequency
        self.interval = 1 / frequency
        self.ser = serial.Serial(port, self.baudrate, timeout=1)
        time.sleep(2)
        self.conn = pymysql.connect(**db_config)
        self.cursor = self.conn.cursor()

        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'sensordata'
        }

        self.running = False
        self.thread = None

        self.temperature_sensor_id = None
        self.accelerometer_id = None

        self.temperature_min_threshold = None
        self.temperature_max_threshold = None

        self.acceleration_min_threshold = None
        self.acceleration_max_threshold = None

        self.acceleration_x2 = 0
        self.acceleration_y2 = 0
        self.acceleration_z2 = 0

    def sendCommand(self, command):
        """
        Sender en kommando til mikrokontrolleren i JSON-format.

        Args:
            command (str): Kommandoen som skal sendes.
        """
        command_json = json.dumps({"Command": command})
        self.ser.write(command_json.encode())
        print(f"Sent: {command_json}")

    def setFrequency(self, frequency):
        """
        Setter målefrekvensen til mikrokontrolleren.

        Args:
            frequency (int): Frekvens i Hz.
        """
        command_json = json.dumps({"GatherFreq": frequency})
        self.ser.write(command_json.encode())
        print(f"Sent: {command_json}")

    def sendCommandStart(self):
        """
        Sender START-kommando for å starte datainnsamling.
        """
        self.sendCommand('START')

    def sendCommandStop(self):
        """
        Sender STOP-kommando for å stoppe datainnsamling.
        """
        self.sendCommand('STOP')

    def insertTemperatureData(self, sensor_id, temperature):
        """
        Lagrer temperatursensorverdier i databasen.

        Args:
            sensor_id (str): Sensorens ID.
            temperature (float): Målt temperatur.
        """
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            self.cursor.execute('''
            INSERT INTO temperaturereadings (sensor_id, timestamp, temperature)
            VALUES (%s, %s, %s)
            ''', (sensor_id, timestamp, temperature))
            self.conn.commit()
            print('Temperature data transferred')
        except pymysql.MySQLError as e:
            print(f"Error: {e}")

    def insertAccelerationData(self, sensor_id, acceleration_x, acceleration_y, acceleration_z, diff_acceleration_x, diff_acceleration_y, diff_acceleration_z):
        """
        Lagrer akselerasjonsdata og differanseverdier i databasen.

        Args:
            sensor_id (str): Sensorens ID.
            acceleration_x/y/z (float): Akselerasjonsverdier.
            diff_acceleration_x/y/z (float): Differanse fra forrige måling.
        """
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            self.cursor.execute('''
            INSERT INTO accelerationreadings (sensor_id, timestamp, acceleration_x, acceleration_y, acceleration_z, diff_acceleration_x, diff_acceleration_y, diff_acceleration_z)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (sensor_id, timestamp, acceleration_x, acceleration_y, acceleration_z, diff_acceleration_x, diff_acceleration_y, diff_acceleration_z))
            self.conn.commit()
            print('Acceleration data transferred')
        except pymysql.MySQLError as e:
            print(f"Error: {e}")

    def insertTemperatureAlarm(self, parameter):
        """
        Lagrer temperaturalarm i databasen basert på siste måling.

        Args:
            parameter (str): Alarmtype (høy/lav).
        """
        self.cursor.execute('SELECT reading_id FROM temperaturereadings ORDER BY reading_id DESC LIMIT 1;')
        reading_id = self.cursor.fetchall()
        try:
            self.cursor.execute('''
            INSERT INTO temperaturealarms (reading_id, parameter)
            VALUES (%s, %s)
            ''', (reading_id, parameter))
            self.conn.commit()
            print('Temperature ALARM transferred')
        except pymysql.MySQLError as e:
            print(f"Error: {e}")

    def insertAccelerationAlarm(self, parameter):
        """
        Lagrer akselerasjonsalarm i databasen basert på siste måling.

        Args:
            parameter (str): Alarmtype (høy/lav per akse).
        """
        self.cursor.execute('SELECT reading_id FROM accelerationreadings ORDER BY reading_id DESC LIMIT 1;')
        reading_id = self.cursor.fetchall()
        try:
            self.cursor.execute('''
            INSERT INTO accelerationalarms (reading_id, parameter)
            VALUES (%s, %s)
            ''', (reading_id, parameter))
            self.conn.commit()
            print('Acceleration ALARM transferred')
        except pymysql.MySQLError as e:
            print(f"Error: {e}")

    def getSensorID(self):
        """
        Leser og lagrer sensor-IDer fra enheten.
        """
        self.sendCommand("RETURN_DATA")
        time.sleep(1)
        data = self.ser.readline().decode().strip()
        jsonSensorData = json.loads(data)
        self.temperature_sensor_id = jsonSensorData['SensorConfiguration']['TemperatureSensor']['Sensor_id']
        self.accelerometer_id = jsonSensorData['SensorConfiguration']['Accelerometer']['Sensor_id']
        print("SenorID found:")
        print("temperature_sensor_id:", self.temperature_sensor_id)
        print("accelerometer_id:", self.accelerometer_id)
        print()

    def getAlarmThresholds1(self):
        """
        Leser grenseverdier for temperatur og akselerasjon fra databasen (alternativ versjon).
        """
        self.cursor.execute('SELECT * FROM alarmthresholds where sensor_id = %s', self.temperature_sensor_id)
        temperature_thresholds = self.cursor.fetchall()
        self.temperature_min_threshold = temperature_thresholds[-1][3]
        self.temperature_max_threshold = temperature_thresholds[-1][4]

        self.cursor.execute('SELECT * FROM alarmthresholds where sensor_id = %s', self.accelerometer_id)
        acceleration_thresholds = self.cursor.fetchall()
        self.acceleration_min_threshold = acceleration_thresholds[-1][3]
        self.acceleration_max_threshold = acceleration_thresholds[-1][4]

        print("Threshold set:")
        print(f"Temperature min/max: {self.temperature_min_threshold}/{self.temperature_max_threshold}")
        print(f"Acceleration min/max: {self.acceleration_min_threshold}/{self.acceleration_max_threshold}")
        print()

    def getAlarmThresholds(self):
        """
        Leser og validerer grenseverdier for temperatur og akselerasjon fra databasen.
        """
        try:
            self.cursor.execute('SELECT * FROM alarmthresholds WHERE sensor_id = %s', (self.temperature_sensor_id,))
            temperature_thresholds = self.cursor.fetchall()
            if temperature_thresholds:
                self.temperature_min_threshold = temperature_thresholds[-1][3]
                self.temperature_max_threshold = temperature_thresholds[-1][4]
            else:
                print("No temperature thresholds found for the given sensor ID")

            self.cursor.execute('SELECT * FROM alarmthresholds WHERE sensor_id = %s', (self.accelerometer_id,))
            acceleration_thresholds = self.cursor.fetchall()
            if acceleration_thresholds:
                self.acceleration_min_threshold = acceleration_thresholds[-1][3]
                self.acceleration_max_threshold = acceleration_thresholds[-1][4]
            else:
                print("No acceleration thresholds found for the given sensor ID")

            print("Threshold set:")
            print(f"Temperature min/max: {self.temperature_min_threshold}/{self.temperature_max_threshold}")
            print(f"Acceleration min/max: {self.acceleration_min_threshold}/{self.acceleration_max_threshold}")
            print()
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
        except IndexError as e:
            print(f"Index error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def processData(self, data):
        """
        Behandler JSON-data mottatt fra sensoren, setter inn verdier og vurderer om alarmer skal utløses.

        Args:
            data (str): JSON-streng med sensordata.
        """
        try:
            dataJson = json.loads(data)
            print(dataJson)

            if "acceleration" and "temperature" in dataJson:
                print("Acceleration and Temperature data received")
                # ... [kode uendret]
                # diff-alarm-loop inkludert

            elif "acceleration" in dataJson:
                print("Acceleration data received")
                # ... [kode uendret]

            elif "temperature" in dataJson:
                print("Temperature data received")
                # ... [kode uendret]

            else:
                print("no valid data recived")

        except json.JSONDecodeError:
            print("Received invalid JSON")

    def stop(self):
        """
        Stopper datainnsamlingen og sender STOP-kommando.
        """
        self.running = False
        self.sendCommandStop()

    def run(self):
        """
        Kjører datainnsamlingsprosedyren og starter tråd for løpende innsamling.
        """
        self.running = True
        print('run')
        self.sendCommandStop()
        time.sleep(1)
        print(self.ser.readline().decode().strip())
        self.setFrequency(self.frequency)
        time.sleep(1)
        print(self.ser.readline().decode().strip())
        time.sleep(1)
        self.getSensorID()
        self.getAlarmThresholds()
        self.sendCommandStart()
        print(self.ser.readline().decode().strip())
        time.sleep(1)

        self.thread = threading.Thread(target=self.collectData)
        self.thread.start()

    def collectData(self):
        """
        Samler inn data kontinuerlig fra den serielle porten og behandler dem.
        """
        try:
            while self.running == True:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode().strip()
                    print(f"Received: {data}")
                    self.processData(data)

                print('sleep')
                time.sleep(self.interval)
                print()
                print()
        except KeyboardInterrupt:
            self.sendCommandStop()
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

if __name__ == "__main__":
    """
    Starter datainnsamling fra sensor på angitt port og frekvens.
    """
    print('wfjlw')
    frequency = 1
    collector = SensorDataCollector(port='COM5', frequency=frequency)

    time.sleep(5)
    collector.run()
    print('thrad')
    time.sleep(10)
    collector.stop()
