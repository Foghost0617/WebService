# main.py - 主应用文件

from fastapi import FastAPI
# 导入 CORS 中间件
from fastapi.middleware.cors import CORSMiddleware 
from router import router as personnel_router


# 创建应用实例
app = FastAPI(
    title="Personnel Management System API",
    version="1.0.0"
)

# --- 🎯 解决 CORS 问题的关键代码 ---
origins = [
    "*", # ⚠️ 允许所有来源进行跨域访问 (本地开发时最简单)
    # 如果你想限制，可以改成：
    # "http://localhost",
    # "http://127.0.0.1",
    # "file://", # 虽然浏览器通常需要 * 来匹配本地文件
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # 允许的来源列表
    allow_credentials=True, # 允许携带 Cookie/授权头
    allow_methods=["*"], # 允许所有 HTTP 方法 (GET, POST, PUT, DELETE, OPTIONS等)
    allow_headers=["*"], # 允许所有请求头
)
# ------------------------------------

# 挂载路由
app.include_router(personnel_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Personnel API"}