# 物联网环境监测系统 (IoT Environmental Monitoring System)

本项目是一个基于 MQTT 协议和 Flask 框架的物联网环境监测系统，集成了数据采集、实时传输、持久化存储、数据分析及 AI 智能建议功能。

## 项目简介

*   **全栈架构**: 涵盖数据发布 (Publisher)、消息代理 (Broker)、数据消费 (Consumer)、后端 API (Backend) 及前端展示 (Frontend)。
*   **实时监测**: 实时展示温度、湿度、气压数据变化趋势。
*   **智能分析**:
    *   **环境状态评估**: 综合分析热舒适度、湿度状态等。
    *   **风险预警**: 基于规则的异常检测与风险评级。
    *   **趋势预测**: 基于时间序列的简单趋势预测。
    *   **AI 智能建议**: 集成 DeepSeek LLM，根据当前环境数据提供自然语言形式的专业改善建议。
*   **数据回放**: 支持模拟历史传感器数据的回放与发布。

## 项目结构

```
2025-Autumn-IoT-Final-Project/
├── backend/                # Flask 后端服务器
│   ├── controller/         # API 路由控制器
│   ├── service/            # 业务逻辑 (分析、预测、风险、LLM)
│   ├── repository/         # 数据库访问层
│   └── app.py              # 后端启动入口
├── frontend/               # 前端可视化界面
│   └── index.html          # 监控仪表盘
├── mqtt_broker/            # MQTT 代理配置
│   └── mosquitto.conf      # Mosquitto 配置文件
├── mqtt_consumer/          # MQTT 数据消费者
│   ├── storage/            # 数据存储逻辑
│   └── consumer.py         # 消费者启动入口
├── publisher/              # 数据发布模拟器
│   ├── publisher_gui.py    # GUI 发布工具
│   └── publisher_state.json
├── data/                   # 模拟传感器数据源 (.txt)
├── database/               # SQLite 数据库文件
└── requirements.txt        # Python 依赖列表
```

## 启动指南

由于代码中使用了相对路径（如 `../database/sensor_data.db`），**必须**进入相应的子目录启动服务，并正确设置 `PYTHONPATH` 以便 Python 能找到模块。

请按照以下顺序打开 **4 个独立的终端窗口** 运行各个服务。

### 1. 环境准备

*   安装 Python 3.8+
*   安装 [Mosquitto MQTT Broker](https://mosquitto.org/download/)
*   安装依赖: `pip install -r requirements.txt`

### 2. 启动 MQTT Broker (Terminal 1)

在项目根目录下运行：

```bash
# 请替换为你的 mosquitto 安装路径(如D:\mosquitto\mosquitto.exe)
你的 mosquitto 安装路径 -c mqtt_broker\mosquitto.conf -v
```

### 3. 启动数据消费者 (Terminal 2)

需要进入 `mqtt_consumer` 目录，并将项目根目录加入 `PYTHONPATH` 以便正确导入模块。

```bash
cd mqtt_consumer
python consumer.py
```

### 4. 启动后端 API (Terminal 3)

需要进入 `backend` 目录，并将项目根目录加入 `PYTHONPATH`。

```bash
cd backend
python app.py
```

### 5. 启动数据发布器 (Terminal 4)

需要进入 `publisher` 目录（以便找到 `../data` 数据文件）。

```bash
cd publisher
python publisher_gui.py
```

### 6. 访问前端

直接在浏览器中打开 `frontend\index.html` 文件。

## 功能说明

### 数据发布器 (Publisher)
*   点击 **"Start Publishing"** 开始发送模拟数据。
*   数据源自 `data/` 目录下的历史记录文件。

### 前端仪表盘
*   **实时图表**: 显示温湿度、气压的实时曲线。
*   **状态分析**: 左下角显示当前环境的舒适度与风险等级。
*   **AI 建议**: 点击 **"AI 智能建议"** 卡片中的 **"分析"** 按钮，获取基于 DeepSeek 大模型的环境改善建议。

## 配置说明

*   **LLM API Key**: 在 `backend/service/llm_service.py` 中配置。
*   **MQTT 配置**: 默认连接 `localhost:1883`。
*   **数据库**: 数据存储于 `database/sensor_data.db` (SQLite)。

## 依赖库

*   `flask`: Web 框架
*   `flask-cors`: 跨域支持
*   `paho-mqtt`: MQTT 客户端
*   `numpy`: 数据分析
*   `requests`: HTTP 请求 (用于 LLM API)
