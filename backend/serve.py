# personnel_service.py - 服务层 (Business Logic)

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from dbCRUD import *
from val import PersonnelCreate, PersonnelUpdate, PersonnelInDB 

# --- 1. 新增人员 (CREATE - POST /personnel) ---
def create_personnel_service(db: Session, person_in: PersonnelCreate) -> PersonnelInDB:
    """
    业务逻辑：新增人员。
    - 检查学号是否已存在 (业务唯一性检查)。
    - 调用 CRUD 层进行创建。
    """
    
    # 1. 业务检查: 检查学号是否已存在
    db_person = get_personnel_by_student_id(db, person_in.id)
    if db_person:
        # 如果学号存在，抛出 409 冲突异常
        raise HTTPException(status_code=409, detail=f"新增失败：学号 {person_in.id} 已存在于系统中。")
        
    # 2. 调用 CRUD 层创建记录 (CRUD 返回 ORM 对象)
    new_person_orm = create_personnel(db, person_in)
    # 3. 将 ORM 对象转换为 Pydantic 响应模型
    return PersonnelInDB.model_validate(new_person_orm)


# --- 2. 查询单个人员 (READ - GET /personnel/{id}) ---
def get_personnel_by_id_service(db: Session, student_id: str) -> PersonnelInDB:
    """
    业务逻辑：根据学号 (id) 查询单个人员。
    - 检查记录是否存在。
    """
    db_person = get_personnel_by_student_id(db, student_id)
    if not db_person:
        # 如果记录不存在，抛出 404 异常
        raise HTTPException(status_code=404, detail=f"查询失败：未找到学号 {student_id} 对应的记录。")
        
    # 将 ORM 对象转换为 Pydantic 响应模型
    return PersonnelInDB.model_validate(db_person)


# --- 3. 查询所有人员 (LIST - GET /personnel) ---
def get_all_personnel_service(db: Session, mode: str = "descend") -> List[PersonnelInDB]:
    """
    业务逻辑：查询所有人员列表。
    - 直接调用 CRUD 层，处理排序逻辑。
    """
    personnel_list_orm = get_all_personnel(db, mode=mode)
    
    # 将 ORM 对象列表转换为 Pydantic 模型列表
    return [PersonnelInDB.model_validate(p) for p in personnel_list_orm]


# --- 4. 修改人员信息 (UPDATE - PUT/PATCH /personnel/{id}) ---
def update_personnel_by_id_service(db: Session, student_id: str, person_update: PersonnelUpdate) -> PersonnelInDB:
    """
    业务逻辑：根据学号 (id) 修改人员信息。
    - 检查请求体中的新学号 (如果存在) 是否与系统中其他记录冲突。
    - 调用 CRUD 层进行更新。
    """
    # 1. 业务检查: 如果请求体中包含新的学号 (id)，需要进行唯一性检查
    if person_update.id is not None and person_update.id != student_id:
        # 查找系统中是否有其他记录使用了这个新学号
        existing_person_with_new_id = get_personnel_by_student_id(db, person_update.id)
        
        if existing_person_with_new_id:
            # 如果找到记录，则冲突（因为不是当前正在更新的记录）
            raise HTTPException(
                status_code=409, 
                detail=f"修改失败：新的学号 {person_update.id} 已被其他记录占用。"
            )

    # 2. 调用 CRUD 层执行更新操作 (使用基于 ID 的 CRUD 函数)
    updated_person_orm = update_personnel_by_student_id(db, student_id, person_update)
    
    if not updated_person_orm:
        # 如果 CRUD 层返回 None，说明原学号不存在
        raise HTTPException(status_code=404, detail=f"修改失败：未找到学号 {student_id} 对应的记录。")

    # 3. 返回 Pydantic 响应模型
    return PersonnelInDB.model_validate(updated_person_orm)


# --- 5. 删除人员 (DELETE - DELETE /personnel/{id}) ---
def delete_personnel_by_id_service(db: Session, student_id: str) -> bool:
    """
    业务逻辑：根据学号 (id) 删除人员。
    - 检查记录是否存在。
    - 调用 CRUD 层执行删除。
    """
    
    # 调用 CRUD 层执行删除操作 (使用基于 ID 的 CRUD 函数)
    is_deleted = delete_personnel_by_student_id(db, student_id)
    
    if not is_deleted:
        # 如果删除失败（CRUD 返回 False），说明学号不存在
        raise HTTPException(status_code=404, detail=f"删除失败：未找到学号 {student_id} 对应的记录。")
        
    return True # 返回 True 表示删除成功