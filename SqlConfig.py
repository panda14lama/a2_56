import mysql.connector # Importerer MySQL-connektoren for å koble til MySQL-databasen

#Etablerer en tilkobling til MySQL - serveren
connection = mysql.connector.connect(
    host="localhost", # Kobler til MySQL-serveren på localhost
    user="root", # Brukernavn for MySQL-serveren
    passwd="rgtt4Lama" # Passord for MySQL-serveren
)

cursorObject = connection.cursor() # Oppretter en cursor for å utføre SQL-spørringer

# Utfører en SQL-kommando for å opprette en ny database kalt "Sensordata"
cursorObject.execute("CREATE DATABASE Sensordata")
# Lukker tilkoblingen til MySQL-serveren
connection.close()

