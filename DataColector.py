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
        time.sleep(2)  # Wait for the connection to establish

        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'sensordata'
        }
        self.conn = pymysql.connect(**self.db_config)
        self.cursor = self.conn.cursor()

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
        Sender en kommando til mikrokontrolleren via seriell port.

        Args:
            command (str): Kommandoen som skal sendes.
        """
        if not self.ser.is_open:
            self.ser.open()
        command_json = json.dumps({"Command": command})
        self.ser.write(command_json.encode())
        print(f"Sent: {command_json}")


    def setFrequency(self, frequency):
        """
        Setter målefrekvensen for datainnsamling.

        Args:
            frequency (int): Antall målinger per sekund.
        """
        command_json = json.dumps({"GatherFreq": frequency})
        self.ser.write(command_json.encode())
        print(f"Sent: {command_json}")

    def sendCommandStart(self):
        """
        Sender kommando til mikrokontrolleren for å starte datainnsamling.
        """
        self.sendCommand('START')

    def sendCommandStop(self):
        """
        Sender kommando til mikrokontrolleren for å stoppe datainnsamling.
        """
        self.sendCommand('STOP')

    def insertTemperatureData(self, sensor_id, temperature):
        """
        Setter inn temperaturdata i databasen.

        Args:
            sensor_id (int): Sensorens ID.
            temperature (float): Temperaturmåling.
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
        Setter inn akselerasjonsdata i databasen.

        Args:
            sensor_id (int): Sensorens ID.
            acceleration_x (float): Akselerasjon i x-retning.
            acceleration_y (float): Akselerasjon i y-retning.
            acceleration_z (float): Akselerasjon i z-retning.
            diff_acceleration_x (float): Differensiell akselerasjon i x-retning.
            diff_acceleration_y (float): Differensiell akselerasjon i y-retning.
            diff_acceleration_z (float): Differensiell akselerasjon i z-retning.
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
        Setter inn temperaturalarm i databasen.

        Args:
            parameter (str): Parameter som utløste alarmen.
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
        Setter inn akselerasjonsalarm i databasen.

        Args:
            parameter (str): Parameter som utløste alarmen.
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
        Henter sensor-IDer fra mikrokontrolleren.
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

    def getAlarmThresholds(self):
        """
        Henter alarmgrenser fra databasen.
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
        Behandler mottatt data fra sensorer, setter inn data i databasen og sjekker for alarmer.

        Args:
            data (str): JSON-streng med sensoravlesninger.
        """
        try:
            dataJson = json.loads(data)

            print(dataJson)
            if "acceleration" and "temperature" in dataJson:
                print("Acceleration and Temperature data received")

                temperature_stamp = dataJson['temperature']
                sensor_id_temp = temperature_stamp['sensor_id']
                temperature = temperature_stamp['temperature']

                self.insertTemperatureData(sensor_id_temp, temperature)

                if temperature > self.temperature_max_threshold:
                    self.insertTemperatureAlarm("HIGH ALARM TEMPERATURE")
                elif temperature < self.temperature_min_threshold:
                    self.insertTemperatureAlarm("LOW ALARM TEMPERATURE")
                else:
                    print("Temperature inside threshold")

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

                self.insertAccelerationData(sensor_id_acc, acceleration_x, acceleration_y, acceleration_z,
                                            diff_acceleration_x, diff_acceleration_y, diff_acceleration_z)

                # Loop to check acceleration differences and insert alarms
                diff_accelerations = {
                    'x': diff_acceleration_x,
                    'y': diff_acceleration_y,
                    'z': diff_acceleration_z
                }

                for axis, diff in diff_accelerations.items():
                    if diff > self.acceleration_max_threshold:
                        self.insertAccelerationAlarm(f"HIGH ALARM ACCELERATION {axis.upper()}")
                    elif diff < self.acceleration_min_threshold:
                        self.insertAccelerationAlarm(f"LOW ALARM ACCELERATION {axis.upper()}")
                    else:
                        print(f"Acceleration {axis.upper()} inside threshold")

            elif "acceleration" in dataJson:
                print("Acceleration data received")
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

                self.insertAccelerationData(sensor_id_acc, acceleration_x, acceleration_y, acceleration_z,
                                            diff_acceleration_x, diff_acceleration_y, diff_acceleration_z)

                # Loop to check acceleration differences and insert alarms
                diff_accelerations = {
                    'x': diff_acceleration_x,
                    'y': diff_acceleration_y,
                    'z': diff_acceleration_z
                }

                for axis, diff in diff_accelerations.items():
                    if diff > self.acceleration_max_threshold:
                        self.insertAccelerationAlarm(f"HIGH ALARM ACCELERATION {axis.upper()}")
                    elif diff < self.acceleration_min_threshold:
                        self.insertAccelerationAlarm(f"LOW ALARM ACCELERATION {axis.upper()}")
                    else:
                        print(f"Acceleration {axis.upper()} inside threshold")

            elif "temperature" in dataJson:
                print("Temperature data received")
                temperature_stamp = dataJson['temperature']
                sensor_id_temp = temperature_stamp['sensor_id']
                temperature = temperature_stamp['temperature']

                self.insertTemperatureData(sensor_id_temp, temperature)

                if temperature > self.temperature_max_threshold:
                    self.insertTemperatureAlarm("HIGH ALARM TEMPERATURE")
                elif temperature < self.temperature_min_threshold:
                    self.insertTemperatureAlarm("LOW ALARM TEMPERATURE")
                else:
                    print("Temperature inside threshold")
            else:
                print("no valid data received")

        except json.JSONDecodeError:
            print("Received invalid JSON")

    def stop(self):
        """
        Stopper datainnsamling og sender stoppkommando til mikrokontrolleren.
        """
        self.running = False
        self.sendCommandStop()
        self.thread = None

    def run(self):
        """
        Starter datainnsamling ved å sende nødvendige kommandoer til mikrokontrolleren og opprette en tråd for datainnsamling.
        """
        self.running = True
        self.conn.ping(reconnect=True)
        print('run')

        self.sendCommandStop()
        time.sleep(1)
        response = self.ser.readline().decode().strip()
        while response != '{"Response":"Data gathering stopped."}':
            response = self.ser.readline().decode().strip()
            print('WRONG RESPONSE: ',response)

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
        Samler inn data fra sensorer i en løkke og behandler dataene.
        """
        try:
            while self.running:
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



if __name__ == "__main__":
    # Set the frequency of the sensor in Hz

    frequency = 1

    collector = SensorDataCollector(port='COM5', frequency=frequency)

    time.sleep(5)
    #collector.sendCommandStart()

    collector.run()

    time.sleep(10)
    collector.stop()
    time.sleep(5)
    collector.run()





#time.sleep(30)
#collector.send_command("STOP")
