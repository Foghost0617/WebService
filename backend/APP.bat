@echo off
REM 查找 client_app.py 的路径
set APP_SCRIPT=client_app.py

REM 执行 Python 脚本，将所有参数传递给它 (%* 代表所有参数)
python "%APP_SCRIPT%" %*