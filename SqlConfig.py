import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="rgtt4Lama"
)

cursorObject = connection.cursor()
cursorObject.execute("CREATE DATABASE Sensordata")
connection.close()

