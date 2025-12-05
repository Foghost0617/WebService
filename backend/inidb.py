import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pymysql


MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"  # 替换为您的 MySQL 用户名
MYSQL_PASSWORD = "118211yao"  # 替换为您的 MySQL 密码
DATABASE_NAME = "xinxi"  # 数据库名称

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

# 2. 创建连接到指定数据库的引擎
engine = create_engine(DATABASE_URL)
Base = declarative_base()


# --- 3. 数据库模型定义 ---
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


# --- 5. 执行脚本 ---
if __name__ == "__main__":
    create_tables()


# # test_crud.py - CRUD 层独立测试

# import sys
# import os
# from sqlalchemy.orm import Session
# from datetime import datetime

# # 假设您的文件结构如下，并调整路径以确保导入正确
# # project_root/cd
# # ├── database.py   (包含 Personnel ORM 模型和 SessionLocal)
# # ├── models.py     (包含 Pydantic 模型 PersonnelCreate, PersonnelUpdate)
# # └── personnel_crud.py (包含 CRUD 函数)
# # └── test_crud.py  (此文件)

# try:
#     # 从您的文件中导入 SessionLocal (会话工厂), Personnel (ORM 模型)
#     from .database import SessionLocal, Personnel
#     # 从您的文件中导入 Pydantic 模型
#     from .val import PersonnelCreate, PersonnelUpdate
#     # 从您的 CRUD 文件中导入 CRUD 函数
#     from .dbCRUD import (
#         create_personnel, 
#         get_personnel_by_pid, 
#         get_personnel_by_student_id,
#         update_personnel, 
#         delete_personnel,
#         get_all_personnel
#     )
# except ImportError as e:
#     print(f"导入失败，请检查文件路径和命名: {e}")
#     input("确保 database.py, models.py, personnel_crud.py 文件存在并能被正确导入。")
#     sys.exit(1)


# # --- 1. 获取测试用的数据库 Session ---
# def get_test_db() -> Session:
#     """获取一个数据库 Session 用于测试"""
#     return SessionLocal()


# # --- 2. 测试函数 ---
# def run_crud_tests():
#     db = get_test_db()
    
#     # 随机生成一个学号，确保唯一性
#     unique_student_id = "1234567890124"

#     print("\n--- CRUD 独立测试开始 ---")
    
#     test_pid = None
    
#     # --- 测试 1: CREATE (新增) ---
#     print("\n[TEST 1] 新增记录 (CREATE)...")
#     try:
#         data_to_create = PersonnelCreate(
#             id=unique_student_id,
#             name="测试新增",
#             email="create@test.com",
#             tel="13900000001",
#             hobby="测试爱好"
#         )
#         new_person = create_personnel(db, data_to_create)
#         test_pid = new_person.pid
#         print(f"PASS: 记录新增成功。PID: {test_pid}, 学号: {new_person.id}")
#     except Exception as e:
#         print(f"FAIL: 新增失败。错误: {e}")
#         return

#     # --- 测试 2: READ by PID (查询) ---
#     print("\n[TEST 2] 根据 PID 查询...")
#     found_by_pid = get_personnel_by_pid(db, test_pid)
#     if found_by_pid and found_by_pid.id == unique_student_id:
#         print(f"PASS: 根据 PID 查询成功。姓名: {found_by_pid.name}")
#     else:
#         print("FAIL: 根据 PID 查询失败或数据不匹配。")

#     # --- 测试 3: READ by Student ID (查询) ---
#     print("\n[TEST 3] 根据学号查询...")
#     found_by_sid = get_personnel_by_student_id(db, unique_student_id)
#     if found_by_sid and found_by_sid.pid == test_pid:
#         print(f"PASS: 根据学号查询成功。PID: {found_by_sid.pid}")
#     else:
#         print("FAIL: 根据学号查询失败或数据不匹配。")
        
#     # --- 测试 4: LIST (列表) ---
#     print("\n[TEST 4] 查询列表 (LIST)...")
#     all_personnel = get_all_personnel(db, mode="descend")
#     if len(all_personnel) > 0 and any(p.pid == test_pid for p in all_personnel):
#         print(f"PASS: 列表查询成功，共 {len(all_personnel)} 条记录。")
#     else:
#         print("FAIL: 列表查询失败或找不到新增的记录。")

#     # --- 测试 5: UPDATE (修改) ---
#     print("\n[TEST 5] 修改记录 (UPDATE)...")
#     update_data = PersonnelUpdate(
#         name="测试修改后的姓名",
#         tel="13900000002"  # 仅修改姓名和电话
#     )
#     updated_person = update_personnel(db, test_pid, update_data)
    
#     if (updated_person and updated_person.name == "测试修改后的姓名" and 
#         updated_person.tel == "13900000002"):
#         print("PASS: 记录修改成功。")
#     else:
#         print("FAIL: 记录修改失败或字段未正确更新。")

#     # --- 测试 6: DELETE (删除) ---
#     print("\n[TEST 6] 删除记录 (DELETE)...")
#     is_deleted = delete_personnel(db, test_pid)
    
#     # 验证删除是否成功
#     if is_deleted and not get_personnel_by_pid(db, test_pid):
#         print("PASS: 记录删除成功。")
#     else:
#         print("FAIL: 记录删除失败或记录仍存在。")

#     print("\n--- CRUD 独立测试结束 ---")
#     db.close()

# if __name__ == "__main__":
#     run_crud_tests()