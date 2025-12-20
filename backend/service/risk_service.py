import numpy as np
from backend.repository.sensor_repository import SensorRepository


class RiskService:

    """
    环境风险评估服务
    目标：判断是否存在“需要关注或干预”的风险
    """

    WINDOW = 12

    @staticmethod
    def assess_environment_risk():
        temps = SensorRepository.get_latest("temperature", RiskService.WINDOW)
        hums = SensorRepository.get_latest("humidity", RiskService.WINDOW)
        press = SensorRepository.get_latest("pressure", RiskService.WINDOW)

        if not temps or not hums or not press:
            return {
                "risk_level": "UNKNOWN",
                "confidence": 0.0,
                "reason": "insufficient data"
            }

        t = np.array([r.value for r in temps])
        h = np.array([r.value for r in hums])
        p = np.array([r.value for r in press])

        # 变化率（斜率）
        dt = np.polyfit(range(len(t)), t, 1)[0]
        dh = np.polyfit(range(len(h)), h, 1)[0]
        dp = np.polyfit(range(len(p)), p, 1)[0]

        reasons = []
        score = 0.0

        # --- 高温高湿风险 ---
        if t[-1] > 32 and h[-1] > 75:
            score += 0.5
            reasons.append("high temperature & humidity")

        # --- 天气突变风险（气压快速下降） ---
        if dp < -0.4:
            score += 0.4
            reasons.append("pressure dropping rapidly")

        # --- 快速变化风险 ---
        if abs(dt) > 0.5 or abs(dh) > 1.0:
            score += 0.2
            reasons.append("rapid environmental change")

        score = min(score, 1.0)

        if score >= 0.7:
            level = "HIGH"
        elif score >= 0.4:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "risk_level": level,
            "confidence": round(score, 2),
            "reason": ", ".join(reasons) if reasons else "environment stable"
        }
