import mysql.connector
connection = mysql.connector.connect(
    host ="localhost",
    user ="root",
    passwd ="Rishaa24",
    database = "sensordata"
)
cursorObject = connection.cursor()
studentRecord = """CREATE TABLE SENSORS (sensor_id INT AUTO_INCREMENT PRIMARY KEY,type VARCHAR(50),
Location VARCHAR(100), Installation_date DATE)"""

studentRecord1 = """CREATE TABLE TEMPERATUREREADINGS (reading_id INT AUTO_INCREMENT PRIMARY KEY,
sensor_id INT AUTO_INCREMENT FOREIGN KEY, timestamp DATETIME, temperature FLOAT)"""

studentRecord2 = """CREATE TABLE ACCERLERATIONREADINGS (reading_id INT AUTO_INCREMENT PRIMARY KEY,
sensor_id INT AUTO_INCREMENT FOREIGN KEY, timestamp DATETIME, accerleration_x FLOAT,
accerleration_y FLOAT,accerleration_z FLOAT, diff_accerleration_x FLOAT, diff_accerleration_y FLOAT,
 diff_accerleration_z FLOAT)"""

studentRecord3 = """CREATE TABLE ALARMTHRESHOLDS (treshold_id INT AUTO_INCREMENT PRIMARY KEY,
sensor_id INT AUTO_INCREMENT FOREIGN KEY,parameter VARCHAR(50),min_value FLOAT,
max_value FLOAT)"""

studentRecord4 = """CREATE TABLE TEMPERATUREALARMS (alarm_id INT AUTO_INCREMENT PRIMARY KEY,
reading_id INT AUTO_INCREMENT FOREIGN KEY,timestamp DATETIME,parameter VARCHAR(50)"""

studentRecord5 = """CREATE TABLE ACCELERATIONALARMS (alarm_id INT AUTO_INCREMENT PRIMARY KEY, 
reading_id INT AUTO_INCREMENT FOREIGN KEY,timestamp DATETIME, parameter VARCHAR(50)"""


cursorObject.execute(studentRecord1,studentRecord2,studentRecord3,studentRecord4,studentRecord5)
connection.close()