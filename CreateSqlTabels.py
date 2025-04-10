import mysql.connector #Importerer MySQL-connektoren
connection = mysql.connector.connect(
    host="localhost", # Kobler til MySQL-serveren på localhost
    user="root", # Brukernavn for MySQL-databasen
    passwd="root", # Passord for MySQL-databasen
    database="sensordata" # Spesifiserer databasen som skal brukes
)

cursorObject = connection.cursor() # Oppretter en cursor for å utføre SQL-spørringer

# Oppretter tabellen SENSORS for å lagre sensordata
studentRecord = """CREATE TABLE SENSORS (
    sensor_id INT PRIMARY KEY,
    type VARCHAR(50),
    location VARCHAR(100),
    installation_date DATE
)"""
cursorObject.execute(studentRecord)# Utfører SQL-kommandoen for å opprette tabellen

# Oppretter tabellen TEMPERATUREREADINGS for temperaturdata
studentRecord1 = """CREATE TABLE TEMPERATUREREADINGS (
    reading_id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT,
    timestamp DATETIME,
    temperature FLOAT,
    FOREIGN KEY (sensor_id) REFERENCES SENSORS(sensor_id)
)"""
cursorObject.execute(studentRecord1) # Utfører SQL-kommandoen for å opprette tabellen

# Oppretter tabellen ACCELERATIONREADINGS for akselerasjonsdata
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
cursorObject.execute(studentRecord2) # Utfører SQL-kommandoen for å opprette tabellen

# Oppretter tabellen ALARMTHRESHOLDS for alarmgrenser
studentRecord3 = """CREATE TABLE ALARMTHRESHOLDS (
    threshold_id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT,
    parameter VARCHAR(50),
    min_value FLOAT,
    max_value FLOAT,
    FOREIGN KEY (sensor_id) REFERENCES SENSORS(sensor_id) 
)"""
cursorObject.execute(studentRecord3)# Utfører SQL-kommandoen for å opprette tabellen

# Oppretter tabellen TEMPERATUREALARMS for temperaturalarmer
studentRecord4 = """CREATE TABLE TEMPERATUREALARMS (
    alarm_id INT AUTO_INCREMENT PRIMARY KEY,
    reading_id INT,
    parameter VARCHAR(50),
    FOREIGN KEY (reading_id) REFERENCES TEMPERATUREREADINGS(reading_id) 
)"""
cursorObject.execute(studentRecord4)# Utfører SQL-kommandoen for å opprette tabellen

# Oppretter tabellen ACCELERATIONALARMS for akselerasjonsalarmer
studentRecord5 = """CREATE TABLE ACCELERATIONALARMS (
    alarm_id INT AUTO_INCREMENT PRIMARY KEY,
    reading_id INT,
    parameter VARCHAR(50),
    FOREIGN KEY (reading_id) REFERENCES ACCELERATIONREADINGS(reading_id) 
)"""
cursorObject.execute(studentRecord5)# Utfører SQL-kommandoen for å opprette tabellen
connection.close()# Lukker tilkoblingen til databasen



