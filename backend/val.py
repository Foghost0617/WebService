from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

# 需要的正则表达式
REGEX_STUDENT_ID = re.compile(r"^\d{13}$")
REGEX_MOBILE = re.compile(r"^1\d{10}$")
REGEX_EMAIL = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class PersonnelBase(BaseModel):
    """用于定义人员信息的核心字段和验证规则"""
    id: str = Field(..., description="学号 (13位纯数字)")
    name: str = Field(..., max_length=8, description="姓名 (不超过8个中文字符)")
    email: str = Field(..., max_length=255, description="邮箱（xxxx@xxx.xx）")
    tel: str = Field(..., description="手机号码 (11位数字)")
    hobby: str = Field(..., max_length=32, description="个人兴趣 (不超过32个中文字符)")

    # 验证学号 (13位纯数字)
    @field_validator('id', mode='before')
    @classmethod
    def validate_student_id(cls, value):
        if not isinstance(value, str):
            raise ValueError('学号必须是字符串')
        # 检查非空和非空白，并使用去除空白后的值
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('学号不能为空或只包含空格。')
        if not REGEX_STUDENT_ID.fullmatch(cleaned_value):
            raise ValueError('学号必须是13位纯数字')
        return cleaned_value # 返回去除空白的值

    # 2. 验证手机号码 (11位，以1开头)
    @field_validator('tel', mode='before')
    @classmethod
    def validate_mobile(cls, value):
        if not isinstance(value, str):
            raise ValueError('手机号码必须是字符串')
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('手机号码不能为空或只包含空格。')
        if not REGEX_MOBILE.fullmatch(cleaned_value):
            raise ValueError('手机号码必须是11位纯数字，且以1开头')
        return cleaned_value

    # 3. 验证邮箱 (包含@和.)
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, value):
        if not isinstance(value, str):
            raise ValueError('邮箱必须是字符串')
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('邮箱不能为空或只包含空格。')
        if not REGEX_EMAIL.fullmatch(cleaned_value):
            raise ValueError('邮箱格式不正确')
        return cleaned_value

    # 验证姓名
    @field_validator('name', mode='before')
    @classmethod
    def validate_name_length(cls, value):
        if not isinstance(value, str):
            raise ValueError('姓名必须是字符串')
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('姓名不能为空或只包含空格。')
        # 简单检查，确保不超过8个中文字符
        if len(cleaned_value) > 8:
            raise ValueError('姓名不能超过8个中文字符')
        return cleaned_value
    
    @field_validator('hobby', mode='before')
    @classmethod
    def validate_hobby_length(cls, value):
        if not isinstance(value, str):
            # 兼容之前 Pydantic 字段定义中的 str = Field(None, ...)
            if value is None:
                raise ValueError('个人兴趣是必填字段')
            raise ValueError('个人兴趣必须是字符串')

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('个人兴趣不能为空或只包含空格。')
            
        if len(cleaned_value) > 32:
            raise ValueError('个人兴趣不能超过32个中文字符')
        return cleaned_value # 返回去除空白的值

    model_config = ConfigDict(from_attributes=True)


class PersonnelCreate(PersonnelBase):
    """新增人员时的请求体模型 (继承 Base，所有字段必填且非空白)"""
    pass

class PersonnelUpdate(BaseModel):
    """修改人员时的请求体模型 (所有字段可选)"""
    # 字段类型保持 Optional[str]，允许不传入，即允许 None
    id: Optional[str] = None
    name: Optional[str] = Field(None, max_length=8)
    email: Optional[str] = Field(None, max_length=255)
    tel: Optional[str] = None
    hobby: Optional[str] = Field(None, max_length=32)

    # 对于可选字段，如果值存在，则调用相应的验证器
    @field_validator('id', mode='before')
    @classmethod
    def validate_optional_student_id(cls, value):
        if value is not None:
            return PersonnelBase.validate_student_id(value)
        return value # 保持 None，允许不更新

    @field_validator('tel', mode='before')
    @classmethod
    def validate_optional_mobile(cls, value):
        if value is not None:
            return PersonnelBase.validate_mobile(value)
        return value
        
    @field_validator('email', mode='before')
    @classmethod
    def validate_optional_email(cls, value):
        if value is not None:
            return PersonnelBase.validate_email(value)
        return value

    @field_validator('name', mode='before')
    @classmethod
    def validate_optional_name(cls, value):
        if value is not None:
            return PersonnelBase.validate_name_length(value)
        return value

    @field_validator('hobby', mode='before')
    @classmethod
    def validate_optional_hobby(cls, value):
        if value is not None:
            return PersonnelBase.validate_hobby_length(value)
        return value
        
    model_config = ConfigDict(from_attributes=True)


class PersonnelInDB(PersonnelBase):
    """数据库中单个人员的响应模型，包含 ID 和时间"""
    pid: int = Field(..., description="内部主键 ID")
    created_time: datetime = Field(..., description="记录创建时间")

    model_config = ConfigDict(from_attributes=True)


class PersonnelCollectionTemplate(BaseModel):
    """用于 collection+json 规范中的 'template' 字段，描述新增/修改时的字段结构"""
    data: List[Dict[str, Any]] = Field(
        default=[
            {"name": "id", "value": ""},
            {"name": "name", "value": ""},
            {"name": "email", "value": ""},
            {"name": "tel", "value": ""},
            {"name": "hobby", "value": ""},
        ],
        description="新增或修改资源时需提交的字段结构"
    )

    

class PersonnelCollection(BaseModel):
    """用于包装列表查询结果的 Pydantic 模型"""
    items: List[PersonnelInDB] = Field(description="人员记录列表")
    count: int = Field(description="记录总数")


# def run_validation_test():
#     print("--- Pydantic 模型自定义验证开始 ---")
#     # --- 成功案例 (所有数据有效) ---
#     valid_data = {
#         "id": "2023000000001",
#         "name": "欧阳修",
#         "email": "test-user_1@sub.example.com",
#         "tel": "13800138000",
#         "hobby": "编程与阅读"
#     }
#     try:
#         person = PersonnelCreate(**valid_data)
#         print("PASS: 案例 1 (有效数据) - 验证通过。")
#         print(f"       数据: ID={person.id}, Tel={person.tel}, Email={person.email}")
#     except ValidationError as e:
#         print("FAIL: 案例 1 (有效数据) - 失败。不应该发生错误。")
#         print(f"       错误详情: {e.errors()}")
#     # --- 失败案例 1：学号格式错误 (12位) ---
#     invalid_id_length = valid_data.copy()
#     invalid_id_length["id"] = "123456789012" 
#     try:
#         PersonnelCreate(**invalid_id_length)
#         print("FAIL: 案例 2 (学号长度错误) - 验证通过，不符合预期。")
#     except ValidationError as e:
#         error_msg = str(e)
#         if "学号必须是13位纯数字" in error_msg:
#              print("PASS: 案例 2 (学号长度错误) - 验证失败，符合预期。")
#         else:
#              print(f"FAIL: 案例 2 (学号长度错误) - 失败。错误类型不符合预期: {e.errors()}")
#     # --- 失败案例 2：手机号格式错误 (不是1开头的11位) ---
#     invalid_mobile_format = valid_data.copy()
#     invalid_mobile_format["tel"] = "23800138000" # 以2开头
#     try:
#         PersonnelCreate(**invalid_mobile_format)
#         print("FAIL: 案例 3 (手机号格式错误) - 验证通过，不符合预期。")
#     except ValidationError as e:
#         error_msg = str(e)
#         if "以1开头" in error_msg:
#              print("PASS: 案例 3 (手机号格式错误) - 验证失败，符合预期。")
#         else:
#              print(f"FAIL: 案例 3 (手机号格式错误) - 失败。错误类型不符合预期: {e.errors()}")

#     # --- 失败案例 3：邮箱格式错误 (缺少@) ---
#     invalid_email_format = valid_data.copy()
#     invalid_email_format["email"] = "testexample.com"
#     try:
#         PersonnelCreate(**invalid_email_format)
#         print("FAIL: 案例 4 (邮箱格式错误) - 验证通过，不符合预期。")
#     except ValidationError as e:
#         error_msg = str(e)
#         if "邮箱格式不正确" in error_msg:
#              print("PASS: 案例 4 (邮箱格式错误) - 验证失败，符合预期。")
#         else:
#              print(f"FAIL: 案例 4 (邮箱格式错误) - 失败。错误类型不符合预期: {e.errors()}")

#     # --- 失败案例 4：姓名超长 (10个中文字符 > 8) ---
#     invalid_name_length = valid_data.copy()
#     invalid_name_length["name"] = "张王李赵钱孙李周吴郑王"
#     try:
#         PersonnelCreate(**invalid_name_length)
#         print("FAIL: 案例 5 (姓名超长) - 验证通过，不符合预期。")
#     except ValidationError as e:
#         error_msg = str(e)
#         if "姓名不能超过8个中文字符" in error_msg:
#              print("PASS: 案例 5 (姓名超长) - 验证失败，符合预期。")
#         else:
#              print(f"FAIL: 案例 5 (姓名超长) - 失败。错误类型不符合预期: {e.errors()}")
#     print("--- 验证结束 ---")
# if __name__ == "__main__":
#     run_validation_test()