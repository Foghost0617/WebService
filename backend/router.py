# personnel_router.py - 路由层

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

# 导入数据库依赖函数
from database import *
# 导入 Pydantic 模型
from val import PersonnelCreate, PersonnelUpdate, PersonnelInDB, PersonnelCollection
# 注意：PersonnelCollection 是用于列表响应的 Pydantic 模型，我们在 val.py 中定义它

# 导入服务层函数
from serve import *

# 创建 FastAPI 路由器
router = APIRouter(
    prefix="/personnel", # 定义所有接口的共同前缀 /personnel
    tags=["Personnel Management"] # 用于 Swagger 文档分组
)

# --- 辅助依赖函数 ---
# 用于获取数据库 Session 的依赖注入
DbDependency = Depends(get_db)


## =================================================================
## 1. POST /personnel (新增人员)
## =================================================================
@router.post(
    "/",
    response_model=PersonnelInDB,
    status_code=status.HTTP_201_CREATED,
    summary="新增人员记录"
)
def create_personnel_route(
    person_in: PersonnelCreate, # 请求体 Pydantic 自动验证输入
    db: Session = DbDependency # 依赖注入数据库 Session
):
    """
    接收人员信息并创建一条新记录。
    - **Pydantic 自动验证输入。**
    - **服务层检查学号唯一性。**
    - 成功返回 201 Created。
    """
    # 直接调用服务层，服务层负责处理业务逻辑和异常（409冲突）
    return create_personnel_service(db, person_in)


## =================================================================
## 2. GET /personnel/{student_id} (查询单条记录)
## =================================================================
@router.get(
    "/{student_id}",
    response_model=PersonnelInDB,
    summary="根据学号查询单条人员记录"
)
def get_personnel_route(
    student_id: str, # URL 路径参数
    db: Session = DbDependency
):
    """
    根据学号查询人员的详细信息。
    - **服务层检查记录是否存在。**
    - 记录不存在返回 404 Not Found。
    """
    # 直接调用服务层，服务层负责处理记录不存在的异常（404）
    return get_personnel_by_id_service(db, student_id)


## =================================================================
## 3. GET /personnel (查询所有记录)
## =================================================================
@router.get(
    "/",
    response_model=PersonnelCollection, # 使用包含列表的集合模型
    summary="查询所有人员记录列表"
)
def get_all_personnel_route(
    db: Session = DbDependency,
    mode: str = "descend" # 可选的查询参数，用于排序
):
    """
    获取系统中所有人员的列表。
    - 支持按 created_time 排序（mode: 'ascend' 或 'descend'）。
    """
    # 调用服务层获取列表
    personnel_list = get_all_personnel_service(db, mode=mode)
    
    # 将列表包装到 PersonnelCollection 模型中返回
    return {"items": personnel_list, "count": len(personnel_list)}


## =================================================================
## 4. PUT /personnel/{student_id} (修改记录)
## =================================================================
@router.put(
    "/{student_id}",
    response_model=PersonnelInDB,
    summary="根据学号修改人员记录"
)
def update_personnel_route(
    student_id: str,
    person_update: PersonnelUpdate, # 请求体 Pydantic 自动验证更新数据
    db: Session = DbDependency
):
    """
    根据学号修改人员记录的非空字段。
    - **服务层检查记录是否存在（404）。**
    - **服务层检查新学号是否冲突（409）。**
    """
    return update_personnel_by_id_service(db, student_id, person_update)


## =================================================================
## 5. DELETE /personnel/{student_id} (删除记录)
## =================================================================
@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT, # 删除成功返回 204
    summary="根据学号删除人员记录"
)
def delete_personnel_route(
    student_id: str,
    db: Session = DbDependency
):
    """
    根据学号删除人员记录。
    - **服务层检查记录是否存在（404）。**
    - 删除成功返回 204 No Content。
    """
    delete_personnel_by_id_service(db, student_id)


