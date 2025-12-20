from dataclasses import dataclass


@dataclass
class SensorRecord:
    timestamp: str
    sensor_type: str
    value: float