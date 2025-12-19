# 物联网环境监测系统 (IoT Environmental Monitoring System)

## 项目简介

本项目是一个完整的物联网环境监测模拟系统，涵盖了从数据采集、传输、存储到前端展示的全流程。系统由以下四个核心模块组成：

1.  **数据发布端 (Publisher)**: 模拟边缘设备，读取预置的传感器数据（温度、湿度、气压）并通过 MQTT 协议发送。
2.  **消息中间件 (MQTT Broker)**: 使用 Mosquitto 作为消息代理，负责数据的转发。
3.  **后端服务器 (Backend)**: 基于 Flask 开发，负责接收 MQTT 数据、存储至 SQLite 数据库，并提供 RESTful API。
4.  **前端仪表盘 (Frontend)**: 基于 HTML/Chart.js 的可视化界面，实时展示环境数据趋势。

## 启动指南 (手动模式)

本指南将指导你如何分步启动系统的各个组件。

### 1. 环境准备

在开始之前，请确保已完成以下准备工作：

*   **Python**: 已安装 Python 3.x。
*   **Mosquitto**: 已安装 Mosquitto MQTT Broker。
*   **依赖库**: 在项目根目录下运行以下命令安装 Python 依赖：
    ```bash
    pip install -r requirements.txt
    ```

### 2. 启动步骤

你需要打开 **3 个独立的终端窗口**来分别运行不同的服务。

#### 第一步：启动 MQTT 消息代理 (Terminal 1)

启动 Mosquitto 服务并加载项目的配置文件。

```bash
# 请确保在项目根目录下运行
# 如果 mosquitto 未在环境变量中，请使用完整路径 (例如: "D:\mosquitto\mosquitto.exe")
mosquitto -c mqtt_broker/mosquitto.conf -v
```

#### 第二步：启动后端服务器 (Terminal 2)

后端负责接收 MQTT 数据并提供 Web API。

```bash
cd backend
python server.py
```
*启动成功后，控制台应显示 `Running on http://127.0.0.1:5000`。*

#### 第三步：启动数据发布模拟器 (Terminal 3)

这是一个 GUI 程序，用于模拟传感器发送数据。

```bash
cd publisher
python publisher_gui.py
```
*运行后会弹出 "IoT Data Publisher" 窗口。*

#### 第四步：打开前端仪表盘

1.  进入 `frontend` 目录。
2.  直接双击 **`index.html`** 文件，使用浏览器打开。

### 3. 使用说明

1.  **开始发送数据**: 在 **Publisher GUI** 窗口中，点击 **"Start Publishing"** 按钮。
2.  **查看监控**: 浏览器中的图表将开始实时更新。点击页面顶部的按钮可切换查看 **温度**、**湿度** 或 **气压** 数据。
