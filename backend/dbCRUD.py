# personnel_crud.py - 数据访问层 (CRUD)
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from typing import List, Optional, Dict, Any
# 从 database.py 导入 ORM 模型
from val import PersonnelCreate, PersonnelUpdate 
from database import Personnel


# CREATE(新增) 
def create_personnel(db: Session, person_in: PersonnelCreate) -> Personnel:
    """
    新增一条人员信息记录。
    :param db: 数据库会话对象
    :param person_in: Pydantic PersonnelCreate 模型（输入数据）
    :return: 新创建的 Personnel ORM 对象
    """
    # 将 Pydantic 输入模型转换为 ORM 模型
    db_person = Personnel(
        id=person_in.id,
        name=person_in.name,
        email=person_in.email,
        tel=person_in.tel,  
        hobby=person_in.hobby
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

# --- READ (查询) ---
def get_personnel_by_pid(db: Session, pid: int) -> Optional[Personnel]:
    """根据内部主键 pid 查询单条记录。"""
    stmt = select(Personnel).where(Personnel.pid == pid)
    return db.execute(stmt).scalars().first()

def get_personnel_by_student_id(db: Session, id: str) -> Optional[Personnel]:
    """根据学号查询单条记录。"""
    stmt = select(Personnel).where(Personnel.id ==id)
    return db.execute(stmt).scalars().first()

def get_all_personnel(db: Session, mode: str = "descend") -> List[Personnel]:
    """
    查询所有人员信息，并按创建时间排序。
    :param mode: "ascend" (升序) 或 "descend" (降序)
    :return: Personnel ORM 对象列表
    """
    stmt = select(Personnel)
    if mode == "ascend":
        stmt = stmt.order_by(Personnel.created_time.asc())
    elif mode == "descend":
        stmt = stmt.order_by(Personnel.created_time.desc())
    # 默认保持降序
    return db.execute(stmt).scalars().all()


def update_personnel_by_student_id(db: Session, id: str, person_update: PersonnelUpdate) -> Optional[Personnel]:
    """
    根据学号 (id) 修改记录的非空字段。
    """
    # 查找现有记录
    db_person = get_personnel_by_student_id(db, id)
    if not db_person:
        return None  # 记录不存在
    # 提取更新数据，排除未设置的字段
    update_data = person_update.model_dump(exclude_unset=True) 
    # 更新字段
    for key, value in update_data.items():
        setattr(db_person, key, value)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

# 删除（根据学号）
def delete_personnel_by_student_id(db: Session, id: str) -> bool:
    """
    根据学号 (id) 删除记录。
    :return: 如果成功删除返回 True，否则返回 False
    """
    db_person = get_personnel_by_student_id(db, id)
    
    if db_person:
        db.delete(db_person)
        db.commit()
        return True
    return False

