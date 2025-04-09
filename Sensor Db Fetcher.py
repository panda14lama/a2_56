import mysql.connector
from datetime import datetime

class SensorDataFetcher:
    def __init__(self, host="localhost", user="root", password="", database="sensordata"):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }

    def get_latest_data(self, temp_sensor_id=1, accel_sensor_id=2):
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)

            # Hent siste temperaturverdi
            cursor.execute("""
                SELECT temperature, sensor_id FROM temperaturereadings
                WHERE sensor_id = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (temp_sensor_id,))
            temp_row = cursor.fetchone()

            # Hent siste akselerasjonsverdi
            cursor.execute("""
                SELECT x, y, z, sensor_id FROM accelerationreadings
                WHERE sensor_id = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (accel_sensor_id,))
            accel_row = cursor.fetchone()

            cursor.close()
            conn.close()

            if temp_row and accel_row:
                thresholds = self.get_thresholds(temp_sensor_id)
                return {
                    "temperature": round(temp_row['temperature'], 2),
                    "x": round(accel_row['x'], 3),
                    "y": round(accel_row['y'], 3),
                    "z": round(accel_row['z'], 3),
                    "thresholds": thresholds
                }
            else:
                return None

        except Exception as e:
            print("Databasefeil:", e)
            return None

    def get_thresholds(self, sensor_id):
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT threshold_type, min_value, max_value
                FROM alarmthresholds
                WHERE sensor_id = %s
            """, (sensor_id,))
            rows = cursor.fetchall()

            cursor.close()
            conn.close()

            thresholds = {}
            for row in rows:
                if row["threshold_type"] == "temp":
                    thresholds["temp_min"] = row["min_value"]
                    thresholds["temp_max"] = row["max_value"]
                elif row["threshold_type"] == "accel":
                    thresholds["accel_threshold"] = max(abs(row["min_value"]), abs(row["max_value"]))
            return thresholds

        except Exception as e:
            print("Feil ved henting av grenseverdier:", e)
            return {
                "temp_min": -4,
                "temp_max": 28,
                "accel_threshold": 15
            }


if __name__ == "__main__":
    fetcher = SensorDataFetcher(password="DittPassordHer")  # Sett riktig passord
    latest_data = fetcher.get_latest_data()
    if latest_data:
        print("Sensorverdier:", latest_data)
        print("Grenseverdier:", latest_data['thresholds'])
    else:
        print("Ingen data funnet.")
    print(fetcher.get_thresholds(sensor_id=1))
