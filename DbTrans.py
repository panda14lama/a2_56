import time
import mysql.connector  # Importerer MySQL-connektoren



class HentData:
    def __init__(self):
        self.diff_acceleration_x = 5
        self.diff_acceleration_y = 2
        self.diff_acceleration_z = 1

        self.temperatur = 5


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

    def return_data(self):

        return {
            "temperature": self.temperatur,
            "x": self.diff_acceleration_x,
            "y": self.diff_acceleration_y,
            "z": self.diff_acceleration_z
        }

    def run(self):

        while True:

            diff_acceleartion = self.hent_diffacc()
            self.diff_acceleration_x = diff_acceleartion[0]['diff_acceleration_x']
            self.diff_acceleration_y = diff_acceleartion[0]['diff_acceleration_y']
            self.diff_acceleration_z = diff_acceleartion[0]['diff_acceleration_z']

            temperatur = self.hent_temperatur()
            self.temperatur = temperatur[0]['temperature']



#data_henter = HentData()


#data_henter.run()
