#Hallonnnnnnn
import mysql.connector
connection = mysql.connector.connect(
    host ="localhost",
    user ="root",
    passwd ="jegerbest",
    database = "msd"
)
# sett inn data i tabellen students
cursorObject = connection.cursor()
sql = "INSERT INTO STUDENTS (STUDENTID, NAME, AGE, GRADE)\
VALUES (%s, %s, %s, %s)"
val = [("1", "Eva Hansen", "20", "A"), ("2", "Lars Olsen", "22", "A"),
("3", "Ingrid Moe", "24", "B"),]
cursorObject.executemany(sql, val)
connection.commit()
connection.close()






