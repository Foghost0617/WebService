# database.py - 包含数据库连接配置和 SQLAlchemy ORM 模型定义

from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime
import pymysql
from zoneinfo import ZoneInfo 

# --- 数据库连接配置 ---
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root" 
MYSQL_PASSWORD = "118211yao" 
DATABASE_NAME = "xinxi" 
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{DATABASE_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 定义东八区时区对象
TIMEZONE_CN = ZoneInfo("Asia/Shanghai")
# 定义一个获取当前东八区时间的可调用函数
def get_now_asia_CN():
    """返回时区感知的东八区当前时间"""
    return datetime.now(TIMEZONE_CN)

# --- SQLAlchemy ORM 模型定义 ---
class Personnel(Base):
    """人员信息表模型 - 数据库映射对象"""
    __tablename__ = 'student'

    pid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id = Column(String(13), unique=True, nullable=False, index=True) 
    name = Column(String(32), nullable=False) 
    email = Column(String(255), nullable=False)
    tel = Column(String(11), nullable=False)
    hobby = Column(String(128),nullable=False)
    created_time = Column(DateTime, default=get_now_asia_CN, nullable=False)
    
# --- 数据库会话依赖函数 ---
def get_db():
    """FastAPI 依赖注入函数，用于获取和关闭数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()