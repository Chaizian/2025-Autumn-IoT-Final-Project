import requests
import json
import os

class LLMService:
    API_KEY = "sk-095aa5ca4ef14a218fcaa0b7e69f96c8"
    API_URL = "https://api.deepseek.com/chat/completions"

    @staticmethod
    def get_advice(status, risk, prediction):
        prompt = LLMService._build_prompt(status, risk, prediction)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLMService.API_KEY}"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个专业的物联网环境监测专家。请根据提供的环境数据，用自然、亲切的口语给出分析和建议。请不要使用Markdown格式（如**加粗**、- 列表等），不要分点列举，直接像聊天一样叙述即可，字数控制在100字以内。"},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        try:
            response = requests.post(LLMService.API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"LLM API Error: {e}")
            return "无法获取 AI 建议，请检查网络或 API 配置。"

    @staticmethod
    def _build_prompt(status, risk, prediction):
        return f"""
请根据以下数据和我对话：

【环境状态】
总体: {status.get('overall_status', '未知')}
热舒适度: {status.get('thermal_comfort', '未知')}
湿度: {status.get('humidity_status', '未知')}
气压: {status.get('pressure_trend', '未知')}

【风险】
等级: {risk.get('risk_level', '未知')}
描述: {risk.get('description', '无')}

【趋势】
温度: {prediction.get('temperature_trend', '未知')}
湿度: {prediction.get('humidity_trend', '未知')}

请用一段话告诉我当前环境怎么样，有什么问题，我该怎么做。不要使用任何格式化符号。
"""
