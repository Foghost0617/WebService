import argparse
import requests 
import sys
from prettytable import PrettyTable

# --- 配置 ---
BASE_URL = "http://127.0.0.1:8000"

# --- 辅助函数 ---

def print_success(message: str):
    """输出成功消息到标准输出"""
    print(f"\n成功: {message}")

def print_failure(message: str):
    """输出失败或警告消息到标准错误"""
    print(f"\n失败: {message}", file=sys.stderr)

def get_full_url(path: str) -> str:
    """构造完整的 API URL"""
    return f"{BASE_URL}{path}"
    
def get_error_message(response: requests.Response) -> str:
    """
    从 FastAPI 响应中提取最简洁的错误信息，并增强对网关错误的解析。
    适用于 requests.Response 对象。
    """
    status_code = response.status_code
    
    # 尝试解析 JSON 响应体
    try:
        error_data = response.json()
        
        # 1. Pydantic 验证错误 (422)
        if status_code == 422 and isinstance(error_data.get('detail'), list):
            validation_errors = []
            for err in error_data['detail']:
                # 移除冗余前缀，保留核心错误信息
                msg = err.get('msg', '未知验证错误').replace('Value error, ', '')
                # 添加字段位置信息
                loc = err.get('loc', [])
                field = loc[-1] if len(loc) > 1 and loc[0] == 'body' else '字段'
                validation_errors.append(f"[{field}] {msg}")
            
            return f"输入验证失败: {'; '.join(validation_errors)}"
    
        # 2. 其他 HTTPException 错误 (404, 409, 500等)
        elif error_data.get('detail'):
            detail = error_data['detail']
            error_detail = detail if isinstance(detail, str) else str(detail)
            return f"业务/应用错误 (状态码: {status_code}): {error_detail}"

    except (ValueError, KeyError, TypeError):
        # 无法解析 JSON 或 JSON 结构不正确
        pass 
    # 3. 网关错误或其他非 JSON 错误 (502, 503, 504)
    response_text = response.text.strip()
    if status_code >= 500:
        if response_text and len(response_text) < 500:
             return f"网关/服务器错误 ({status_code})。响应内容: {response_text}"
        
        if status_code == 502:
            return f"502 Bad Gateway。通常是后端服务崩溃或网关配置错误。请检查Uvicorn终端是否有报错。"
        elif status_code == 504:
            return f"504 Gateway Timeout。后端服务超时未响应。请检查服务性能。"
        else:
            return f"服务器返回错误 (状态码: {status_code})."
    
    return f"请求未成功 (状态码: {status_code})."


# --- 核心 API 接口 (使用 requests 同步模式) ---

def api_add(data: dict):
    """添加新条目 (POST /personnel/)"""
    url = get_full_url("/personnel/")
    try:
        # requests.post 是同步操作
        response = requests.post(url, json=data, timeout=10.0)
        
        if response.status_code == 201:
            person = response.json()
            print_success(f"人员添加成功! 学号: {person['id']}, 姓名: {person['name']}")
        else:
            print_failure(f"添加失败: {get_error_message(response)}")
            
    except requests.exceptions.RequestException as e: 
        print_failure(f"网络请求失败: 无法连接到服务器 {BASE_URL}. 错误: {e}")

def api_delete(student_id: str):
    """删除条目 (DELETE /personnel/{id})"""
    url = get_full_url(f"/personnel/{student_id}")
    try:
        response = requests.delete(url, timeout=10.0)
        
        if response.status_code == 204:
            print_success(f"人员 (学号: {student_id}) 删除成功!")
        elif response.status_code == 404:
            print_failure(f"删除失败: 学号 {student_id} 不存在。")
        else:
            print_failure(f"删除失败: {get_error_message(response)}")
            
    except requests.exceptions.RequestException as e:
        print_failure(f"网络请求失败: 无法连接到服务器 {BASE_URL}. 错误: {e}")

def api_update(student_id: str, data: dict):
    """修改条目 (PUT /personnel/{id})"""
    url = get_full_url(f"/personnel/{student_id}")
    try:
        response = requests.put(url, json=data, timeout=10.0)
        
        if response.status_code == 200:
            person = response.json()
            print_success(f"人员 (学号: {student_id}) 修改成功! 姓名: {person['name']}")
        elif response.status_code == 404:
            print_failure(f"修改失败: 学号 {student_id} 不存在。")
        else:
            print_failure(f"修改失败: {get_error_message(response)}")
            
    except requests.exceptions.RequestException as e:
        print_failure(f"网络请求失败: 无法连接到服务器 {BASE_URL}. 错误: {e}")

def api_list(mode: str):
    """列出所有条目 (GET /personnel/?mode={mode})"""
    url = get_full_url(f"/personnel/?mode={mode}")
    try:
        response = requests.get(url, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            print(f"\n--- 人员列表 (排序: {mode.upper()}) ---")
            if not items:
                print("系统中没有记录。")
                return
            
            table = PrettyTable()
            table.field_names = ["序号", "学号 (ID)", "姓名", "电话", "邮箱", "兴趣爱好", "创建时间"]
            
            for index, p in enumerate(items, 1):
                time_str = p.get('created_time', 'N/A')
                if time_str != 'N/A':
                    time_str = time_str[:19].replace('T', ' ')
                    
                table.add_row([
                    index,
                    p.get('id', 'N/A'),
                    p.get('name', 'N/A'),
                    p.get('tel', 'N/A'),
                    p.get('email', 'N/A'),
                    p.get('hobby', 'N/A'),
                    time_str
                ])
            
            print(table)
            print(f"{len(items)} rows in set.")

        else:
            print_failure(f"获取列表失败: {get_error_message(response)}")
            
    except requests.exceptions.RequestException as e:
        print_failure(f"网络请求失败: 无法连接到服务器 {BASE_URL}. 错误: {e}")


# --- 参数解析和主执行逻辑 (保持不变) ---

def parse_and_run():
    epilog_text = """
调用示例:
# 输出用法帮助
App -h      

# 增加一条新记录
App -a -n "张三" -i "2020123456789" -m "13355555555" -e "zhangsan@mail.com" -b "宅家"

# 删除一条记录
App --delete=2020123456789

# 按照时间升序方式输出全部记录
App -l ascend

# 对某条目修改手机号和兴趣爱好
App -u 2020123456789 --mobile="15922223333" -b "健身"
"""

    parser = argparse.ArgumentParser(
        description="人员信息管理客户端App，通过命令行操作FastAPI后端。",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog_text
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-a', '--add', action='store_true', help='增加一条新的条目 (需要联合使用 -n, -i, -m, -e, -b)')
    group.add_argument('-d', '--delete', type=str, metavar='ID', help='对编号ID的条目删除操作 (参数为学号ID)')
    group.add_argument('-u', '--update', type=str, metavar='ID', help='对编号ID的条目修改内容 (参数为学号ID，需要联合使用至少一个更新选项)')
    group.add_argument('-l', '--list', type=str, nargs='?', const='descend', 
                        choices=['descend', 'ascend'], metavar='MODE',
                        help='输出所有条目列表。MODE: ascend (升序) 或 descend (降序，默认)')

    parser.add_argument('-n', '--name', type=str, help='姓名')
    parser.add_argument('-i', '--id', type=str, help='学号')
    parser.add_argument('-m', '--mobile', type=str, help='手机号 tel')
    parser.add_argument('-e', '--email', type=str, help='邮箱') 
    parser.add_argument('-b', '--hobby', type=str, help='兴趣爱好')

    args = parser.parse_args()
    
    # ------------------ 命令行逻辑判断 ------------------
    
    main_actions = [args.add, args.delete, args.update, args.list is not None]
    
    if not any(main_actions):
        args.list = 'descend'

    if args.add:
        required_fields = [args.name, args.id, args.mobile, args.email, args.hobby]
        if not all(required_fields):
            print_failure("增加 (-a) 操作必须同时提供 -n, -i, -m, -e, -b 五个选项。请使用 -h 查看用法。")
            sys.exit(1)
        
        data = {
            "name": args.name,
            "id": args.id,
            "tel": args.mobile, 
            "email": args.email,
            "hobby": args.hobby
        }
        api_add(data) # 直接调用同步函数
        return

    if args.update:
        update_data = {}
        if args.name is not None: update_data['name'] = args.name
        if args.id is not None: update_data['id'] = args.id
        if args.mobile is not None: update_data['tel'] = args.mobile
        if args.email is not None: update_data['email'] = args.email
        if args.hobby is not None: update_data['hobby'] = args.hobby
        
        if not update_data:
            print_failure("修改 (-u ID) 操作必须至少提供 -n, -i, -m, -e, 或 -b 中的一个选项。请使用 -h 查看用法。")
            sys.exit(1)

        api_update(args.update, update_data) # 直接调用同步函数
        return

    if args.delete:
        api_delete(args.delete) # 直接调用同步函数
        return

    if args.list:
        api_list(args.list) # 直接调用同步函数
        return

if __name__ == "__main__":
    try:
        parse_and_run()
    except ImportError as e:
        print_failure(f"缺少必要的库。请运行: pip install requests prettytable")
        sys.exit(1)