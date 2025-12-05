# WHU 信息系统实习作业存档WebService

## 一、项目概述

本项目是一个基于 **FastAPI (Python)** 后端和 **原生 Web 技术 (HTML/CSS/JS)** 前端的简易人员信息管理系统。同时提供了一个独立的命令行客户端，用于后端交互测试。

### 核心技术栈

* **后端 API:** **FastAPI** (Python)
* **前端 Web:** **HTML**, **CSS**, **JavaScript** (无框架)
* **客户端:** 命令行脚本 (`/backend/client_app.py`)
* **示例数据:** **JSON 文件** (`/backend/data/`)

---

## 项目启动与使用

### 1. 启动后端 API 服务 (Uvicorn)
这是整个系统的核心，必须首先启动。
1.  **打开终端/命令行** (CMD 或 PowerShell)。
2.  **切换到后端目录**：
    ```bash
    cd backend
    ```
3.  **运行服务**：
    ```bash
    uvicorn main:app --reload
    ```
    * **提示:** 看到 `Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)` 类似的输出即表示启动成功。

### 2. 访问 Web 网页客户端
后端启动后，即可通过浏览器访问前端页面进行信息收集。
* **文件位置：** `/front/index.html`
* **操作：** 直接在文件管理器中找到该文件并双击用浏览器打开。
---

### 3.客户端 APP 使用 (命令行测试)
一个独立的 Python 客户端程序。
```bash
cd backend
APP -h
```
