import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root"
)

cursorObject = connection.cursor()
cursorObject.execute("CREATE DATABASE Sensordata")
connection.close()

