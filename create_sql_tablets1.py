import mysql.connector
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="sensordata"
)

cursorObject = connection.cursor()

studentRecord = """CREATE TABLE SENSORS (
    sensor_id INT PRIMARY KEY,
    type VARCHAR(50),
    location VARCHAR(100),
    installation_date DATE
)"""
cursorObject.execute(studentRecord)

studentRecord1 = """CREATE TABLE TEMPERATUREREADINGS (
    reading_id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT,
    timestamp DATETIME,
    temperature FLOAT,
    FOREIGN KEY (sensor_id) REFERENCES SENSORS(sensor_id)
)"""
cursorObject.execute(studentRecord1)

studentRecord2 = """CREATE TABLE ACCELERATIONREADINGS (
    reading_id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT,
    timestamp DATETIME,
    acceleration_x FLOAT,
    acceleration_y FLOAT,
    acceleration_z FLOAT,
    diff_acceleration_x FLOAT,
    diff_acceleration_y FLOAT,
    diff_acceleration_z FLOAT,
    FOREIGN KEY (sensor_id) REFERENCES SENSORS(sensor_id) 
)"""
cursorObject.execute(studentRecord2)

studentRecord3 = """CREATE TABLE ALARMTHRESHOLDS (
    threshold_id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT,
    parameter VARCHAR(50),
    min_value FLOAT,
    max_value FLOAT,
    FOREIGN KEY (sensor_id) REFERENCES SENSORS(sensor_id) 
)"""
cursorObject.execute(studentRecord3)

studentRecord4 = """CREATE TABLE TEMPERATUREALARMS (
    alarm_id INT AUTO_INCREMENT PRIMARY KEY,
    reading_id INT,
    parameter VARCHAR(50),
    FOREIGN KEY (reading_id) REFERENCES TEMPERATUREREADINGS(reading_id) 
)"""
cursorObject.execute(studentRecord4)

studentRecord5 = """CREATE TABLE ACCELERATIONALARMS (
    alarm_id INT AUTO_INCREMENT PRIMARY KEY,
    reading_id INT,
    parameter VARCHAR(50),
    FOREIGN KEY (reading_id) REFERENCES ACCELERATIONREADINGS(reading_id) 
)"""
cursorObject.execute(studentRecord5)
connection.close()


