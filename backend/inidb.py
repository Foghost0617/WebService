import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pymysql


MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root" 
MYSQL_PASSWORD = "118211yao"  
DATABASE_NAME = "xinxi"  

# SQLAlchemy 数据库 URL： 'mysql+pymysql://user:password@host:port/database_name'
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{DATABASE_NAME}"


try:
    engine_no_db = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/",
        isolation_level="AUTOCOMMIT"
    )
    with engine_no_db.connect() as connection:
        # 尝试创建数据库，如果已存在会忽略错误
        connection.execute(sqlalchemy.text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
    print(f"数据库 '{DATABASE_NAME}' 创建成功或已存在。")
except Exception as e:
    print(f"数据库连接或创建失败: {e}")
    exit()


engine = create_engine(DATABASE_URL)
Base = declarative_base()


class Personnel(Base):
    """人员信息表模型"""
    __tablename__ = 'student'

    # 内部主键，自增
    pid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 学号，唯一索引
    id = Column(String(13), unique=True, nullable=False, index=True) 
    # 姓名 (最多8个中文字符)
    name = Column(String(32), nullable=False) 
    # 邮箱
    email = Column(String(255), nullable=False)
    # 手机号码 (11位)
    tel = Column(String(11), nullable=False)
    # 兴趣爱好 (最多32个中文字符)
    hobby = Column(String(128),nullable=False)
    
    # 记录创建时间，可以用于排序
    created_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    # def __repr__(self):
    #     return f"<student(pid={self.pid}, student_id='{self.student_id}', name='{self.name}')>"


def create_tables():
    """使用 Base.metadata 创建所有已定义的表"""
    try:
        # 如果表已存在，删除重新建
        Base.metadata.drop_all(bind=engine)
        print("旧表删除完成。")
        Base.metadata.create_all(bind=engine)
        print("数据库表 'student' 创建成功或已存在。")
    except Exception as e:
        print(f"表创建失败: {e}")


if __name__ == "__main__":
    create_tables()
