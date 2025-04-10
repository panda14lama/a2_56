import time
import mysql.connector  # Importerer MySQL-connektoren



class HentData:
    def __init__(self):

        try:
            self.db = mysql.connector.connect(
                host="localhost",  # Kobler til MySQL-serveren på localhost
                user="root",  # Brukernavn for databasen
                password="root",  # Passord for databasen
                database="sensordata",  # Spesifiserer databasen som skal brukes
                auth_plugin =  'mysql_native_password' # Specify the authentication plugin

            )
            self.cursor = self.db.cursor(dictionary=True)  # Oppretter en cursor for å utføre spørringer
        except mysql.connector.Error as err:
            print(f"Error: {err}")  # Viser feilmelding hvis tilkobling mislykkes
            self.db = None
            self.cursor = None

    def hent_temperatur(self):
        if self.cursor:  # Sjekker om tilkobling til databasen er vellykket
            print('cursor')
            self.cursor.execute(
                "SELECT temperature FROM sensordata.temperaturereadings ORDER BY reading_id DESC  LIMIT 1;")  # Utfører SQL-spørring

            temprature = self.cursor.fetchall()  # Henter alle resultatene fra spørringen'

            return temprature
        return None  # Returnerer None hvis spørringen mislykkes

    def hent_diffacc(self):
        if self.cursor:  # Sjekker om tilkobling til databasen er vellykket
                self.cursor.execute(
                    "SELECT diff_acceleration_x,diff_acceleration_y,diff_acceleration_z FROM sensordata.accelerationreadings ORDER BY reading_id DESC LIMIT 1;")  # Utfører SQL-spørring

                diffacc = self.cursor.fetchall()  # Henter alle resultatene fra spørringen
                return diffacc
        return None

    def hent_threshold_temp(self):
        if self.cursor:
            self.cursor.execute(
                """SELECT min_value, max_value  FROM sensordata.alarmthresholds where parameter = "T" order by threshold_id desc limit 1;""")

            threshold_temp = self.cursor.fetchall()
            self.db.commit()
            return threshold_temp
        return None

    def hent_threshold_acc(self):
        if self.cursor:
            self.cursor.execute(
                """SELECT max_value  FROM sensordata.alarmthresholds where parameter = "A" order by threshold_id desc limit 1;""")

            threshold_acc = self.cursor.fetchall()
            self.db.commit()
            return threshold_acc
        return None


    def return_data(self):
        diff_acceleartion = self.hent_diffacc()
        print(diff_acceleartion)

        diff_acceleration_x = diff_acceleartion[0]['diff_acceleration_x']
        diff_acceleration_y = diff_acceleartion[0]['diff_acceleration_y']
        diff_acceleration_z = diff_acceleartion[0]['diff_acceleration_z']

        temperatur = self.hent_temperatur()
        temperatur = temperatur[0]['temperature']
        self.db.commit()

        return {
            "temperature": temperatur,
            "x": diff_acceleration_x,
            "y": diff_acceleration_y,
            "z": diff_acceleration_z
        }




if __name__ == "__main__":
    data_henter = HentData()
    a = data_henter.hent_threshold_temp()
    print(a)
    #data_henter.run()
