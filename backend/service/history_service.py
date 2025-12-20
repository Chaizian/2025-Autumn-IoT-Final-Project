from backend.repository.sensor_repository import SensorRepository


class HistoryService:

    @staticmethod
    def get_history(sensor_type: str, limit: int, group_by: str):
        rows = SensorRepository.query_history(sensor_type, limit, group_by)

        # 按时间正序返回（与你原来的 reversed(data) 等价）
        rows = list(reversed(rows))

        result = []
        for row in rows:
            result.append({
                "timestamp": row[0],
                "value": row[1]
            })

        return result