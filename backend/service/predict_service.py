import numpy as np
from backend.repository.sensor_repository import SensorRepository


class PredictService:

    @staticmethod
    def _predict_series(values, horizon):
        """
        对时间序列做线性预测
        """
        x = np.arange(len(values))
        y = np.array(values)

        coef = np.polyfit(x, y, 1)
        model = np.poly1d(coef)

        future_x = np.arange(len(values), len(values) + horizon)
        future_y = model(future_x)

        slope = coef[0]
        if slope > 0.05:
            trend = "RISING"
        elif slope < -0.05:
            trend = "FALLING"
        else:
            trend = "STABLE"

        return trend, future_y.tolist()

    @staticmethod
    def predict_environment(window=20, horizon=5):
        temps = SensorRepository.get_latest("temperature", window)
        hums = SensorRepository.get_latest("humidity", window)
        press = SensorRepository.get_latest("pressure", window)

        if not temps or not hums or not press:
            return {"error": "insufficient data"}

        t_vals = [r.value for r in temps]
        h_vals = [r.value for r in hums]
        p_vals = [r.value for r in press]

        t_trend, t_future = PredictService._predict_series(t_vals, horizon)
        h_trend, h_future = PredictService._predict_series(h_vals, horizon)
        p_trend, p_future = PredictService._predict_series(p_vals, horizon)

        # 综合判断
        if p_trend == "FALLING":
            overall = "POSSIBLE_WEATHER_CHANGE"
        elif t_trend == "RISING" and t_future[-1] > 30:
            overall = "POSSIBLE_HEAT_DISCOMFORT"
        else:
            overall = "STABLE"

        return {
            "window": window,
            "horizon": horizon,
            "prediction": {
                "temperature": {
                    "current": round(t_vals[-1], 2),
                    "trend": t_trend,
                    "future": [round(v, 2) for v in t_future]
                },
                "humidity": {
                    "current": round(h_vals[-1], 2),
                    "trend": h_trend,
                    "future": [round(v, 2) for v in h_future]
                },
                "pressure": {
                    "current": round(p_vals[-1], 2),
                    "trend": p_trend,
                    "future": [round(v, 2) for v in p_future]
                }
            },
            "overall_trend": overall
        }
