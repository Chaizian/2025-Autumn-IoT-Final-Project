from dataclasses import dataclass


@dataclass
class SensorRecord:
    timestamp: str
    sensor_type: str
    value: float

    @staticmethod
    def from_dict(d: dict):
        return SensorRecord(
            timestamp=d["timestamp"],
            sensor_type=d["type"],
            value=float(d["value"])
        )
