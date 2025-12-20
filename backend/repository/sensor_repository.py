import sqlite3
from backend.model.sensor_record import SensorRecord

DB_PATH = "../database/sensor_data.db"


class SensorRepository:

    @staticmethod
    def get_latest(sensor_type: str, limit: int = 20):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT timestamp, type, value
                       FROM readings
                       WHERE type = ?
                       ORDER BY timestamp DESC
                           LIMIT ?
                       """, (sensor_type, limit))

        rows = cursor.fetchall()
        conn.close()

        return [
            SensorRecord(timestamp=r[0], sensor_type=r[1], value=r[2])
            for r in reversed(rows)
        ]

    @staticmethod
    def query_history(sensor_type: str, limit: int, group_by: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if group_by == "hour":
            query = """
                    SELECT substr(timestamp, 1, 13) AS ts, AVG(value)
                    FROM readings
                    WHERE type=?
                    GROUP BY ts
                    ORDER BY ts DESC
                        LIMIT ? \
                    """
            cursor.execute(query, (sensor_type, limit))

        elif group_by == "day":
            query = """
                    SELECT substr(timestamp, 1, 10) AS ts, AVG(value)
                    FROM readings
                    WHERE type=?
                    GROUP BY ts
                    ORDER BY ts DESC
                        LIMIT ? \
                    """
            cursor.execute(query, (sensor_type, limit))

        else:  # raw
            query = """
                    SELECT timestamp, value
                    FROM readings
                    WHERE type=?
                    ORDER BY timestamp DESC
                        LIMIT ? \
                    """
            cursor.execute(query, (sensor_type, limit))

        rows = cursor.fetchall()
        conn.close()

        return rows
