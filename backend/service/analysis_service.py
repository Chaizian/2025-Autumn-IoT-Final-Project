import numpy as np

from backend.repository.sensor_repository import SensorRepository


class AnalysisService:
    """
     环境状态分析服务
     目标：把原始传感器数据 → 人可理解的环境状态
     """

    WINDOW = 12  # 最近 12 个点（约 1 小时，取决于采样频率）

    @staticmethod
    def _trend(values):
        """计算趋势：上升 / 下降 / 稳定"""
        if len(values) < 5:
            return "UNKNOWN"

        slope = np.polyfit(range(len(values)), values, 1)[0]

        if slope > 0.05:
            return "RISING"
        elif slope < -0.05:
            return "FALLING"
        else:
            return "STABLE"

    @staticmethod
    def get_environment_status():
        temps = SensorRepository.get_latest("temperature", AnalysisService.WINDOW)
        hums = SensorRepository.get_latest("humidity", AnalysisService.WINDOW)
        press = SensorRepository.get_latest("pressure", AnalysisService.WINDOW)

        if not temps or not hums or not press:
            return {"state": "INSUFFICIENT_DATA"}

        t_vals = np.array([r.value for r in temps])
        h_vals = np.array([r.value for r in hums])
        p_vals = np.array([r.value for r in press])

        # 当前值
        t_now = t_vals[-1]
        h_now = h_vals[-1]

        # --- 温热舒适度 ---
        if t_now >= 30:
            thermal = "HOT"
        elif t_now <= 10:
            thermal = "COLD"
        else:
            thermal = "COMFORTABLE"

        # --- 湿度状态 ---
        if h_now >= 70:
            humidity = "HUMID"
        elif h_now <= 30:
            humidity = "DRY"
        else:
            humidity = "NORMAL"

        # --- 气压趋势 ---
        pressure_trend = AnalysisService._trend(p_vals)

        # --- 综合状态 ---
        if thermal != "COMFORTABLE" or humidity != "NORMAL":
            overall = "DISCOMFORT"
        elif pressure_trend == "FALLING":
            overall = "WEATHER_CHANGE"
        else:
            overall = "NORMAL"

        return {
            "thermal_comfort": thermal,
            "humidity_state": humidity,
            "pressure_trend": pressure_trend,
            "overall_state": overall,
            "snapshot": {
                "temperature": round(float(t_now), 2),
                "humidity": round(float(h_now), 2),
                "pressure": round(float(p_vals[-1]), 2)
            }
        }
