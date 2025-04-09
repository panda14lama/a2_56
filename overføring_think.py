import mysql.connector  # Importerer MySQL-connektoren
import numpy as np

class HentData:
    def __init__(self):
        self.diff_acceleration_x = {dx}
        self.diff_acceleration_y = {dy}
        self.diff_acceleration_z = {dz}

        self.


        try:
            self.db = mysql.connector.connect(
                host="localhost",  # Kobler til MySQL-serveren på localhost
                user="root",  # Brukernavn for databasen
                password="root",  # Passord for databasen
                database="sensordata"  # Spesifiserer databasen som skal brukes
            )
            self.cursor = self.db.cursor(dictionary=True)  # Oppretter en cursor for å utføre spørringer
        except mysql.connector.Error as err:
            print(f"Error: {err}")  # Viser feilmelding hvis tilkobling mislykkes
            self.db = None
            self.cursor = None

    def hent_temperatur(self):
        if self.cursor:  # Sjekker om tilkobling til databasen er vellykket
            self.cursor.execute(
                "SELECT temperature FROM sensordata.temperaturereadings WHERE sensor_id = 1 LIMIT 1;")  # Utfører SQL-spørring
            return self.cursor.fetchall()  # Henter alle resultatene fra spørringen
        return None  # Returnerer None hvis spørringen mislykkes
    def hent_diffacc(self):
        if self.cursor:  # Sjekker om tilkobling til databasen er vellykket
                self.cursor.execute(
                    "SELECT diff_acceleration_x,diff_acceleration_y,diff_acceleration_z FROM sensordata.accelerationreadings WHERE sensor_id = 2 LIMIT 1;")  # Utfører SQL-spørring
                return self.cursor.fetchall()  # Henter alle resultatene fra spørringen
        result = self.cursor.fetchall()
        if result:
            dx, dy, dz = result
            print(f"diff_acceleration_x{dx}")
            print(f"diff_acceleration_x{dy}")
            print(f"diff_acceleration_x{dz}")

        else:
            print("Ingen acc data funnet")
            return None  # Returnerer None hvis spørringen mislykkes


# Eksempel på bruk av klassen
data_henter = HentData()
temperatur = data_henter.hent_temperatur()  # Henter temperaturdata fra MySQL
diff_acceleration_x = data_henter.hent_diffacc()
data_henter.send_til_thinkter(temperatur)  # Sender hentet data til Thinkter-serveren

"""

"""
