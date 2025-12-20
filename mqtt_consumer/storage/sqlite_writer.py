import sqlite3
from mqtt_consumer.model.sensor_record import SensorRecord

DB_PATH = "../database/sensor_data.db"


class SQLiteWriter:

    @staticmethod
    def save(record: SensorRecord):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS readings (
                                                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                               timestamp TEXT,
                                                               type TEXT,
                                                               value REAL
                       )
                       """)

        cursor.execute("""
                       INSERT INTO readings (timestamp, type, value)
                       VALUES (?, ?, ?)
                       """, (record.timestamp, record.sensor_type, record.value))

        conn.commit()
        conn.close()