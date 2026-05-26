#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RSOD 遥感目标检测平台 - 通用一键启动脚本
功能:
1. 检测前后端及数据库端口占用情况
2. 自动启动 Docker Compose 数据库与存储服务 (Postgres, Redis, MinIO)
3. 自动检测并激活 rsod-web Conda 虚拟环境
4. 并行启动后端 FastAPI 服务与前端 Vite 调试服务器
5. 实时合并并标记前后端日志输出
6. 支持 Ctrl+C 优雅关闭所有子进程，解决 Windows 环境下的进程残留与端口占用问题
"""

import os
import sys
import time
import socket
import subprocess
import threading

# 端口配置
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
DOCKER_PORTS = [5432, 6379, 9000, 9001]

# ANSI 终端颜色定义
COLOR_GREEN = "\033[92m"
COLOR_CYAN = "\033[96m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"

def log_system(msg):
    print(f"{COLOR_GREEN}[System] {msg}{COLOR_RESET}")

def log_warn(msg):
    print(f"{COLOR_YELLOW}[Warning] {msg}{COLOR_RESET}")

def log_error(msg):
    print(f"{COLOR_RED}[Error] {msg}{COLOR_RESET}")

# 记录当前运行的子进程
running_processes = []

def is_port_in_use(port, host='127.0.0.1'):
    """检查指定端口是否已被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((host, port)) == 0

def check_ports():
    """进行启动前的端口检测"""
    log_system("正在进行端口占用情况预检...")
    
    # 核心服务端口冲突检查
    if is_port_in_use(BACKEND_PORT):
        log_error(f"后端服务端口 {BACKEND_PORT} 已被占用！请先释放该端口后再启动。")
        return False
        
    if is_port_in_use(FRONTEND_PORT):
        log_error(f"前端开发服务端口 {FRONTEND_PORT} 已被占用！请先释放该端口后再启动。")
        return False
        
    # Docker 容器端口占用提示
    docker_occupied = []
    for port in DOCKER_PORTS:
        if is_port_in_use(port):
            docker_occupied.append(port)
            
    if docker_occupied:
        log_system(f"检测到 Docker 端口 {docker_occupied} 已被占用（这通常意味着 Docker 容器已在后台运行，系统将继续启动）")
    else:
        log_system("Docker 依赖端口未被占用，准备拉起容器服务...")
        
    return True

def start_docker_services():
    """启动 Docker Compose 服务"""
    log_system("正在拉起 Docker Compose 数据库及存储服务 (PostgreSQL, Redis, MinIO)...")
    
    # 兼容两种 docker compose 命令格式
    commands = [
        ["docker", "compose", "up", "-d"],
        ["docker-compose", "up", "-d"]
    ]
    
    success = False
    for cmd in commands:
        try:
            # 运行命令并等待完成，指定 utf-8 编码和 ignore 避免 Windows 环境下解码错误
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore", check=True)
            log_system("Docker Compose 服务启动/更新成功。")
            success = True
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
            
    if not success:
        log_warn("无法通过 Docker 启动数据库服务。请确保 Docker Desktop 已运行，或本地已手动启动 PostgreSQL, Redis 和 MinIO。")

def find_python_interpreter():
    """寻找合适的 Python 解释器，确保使用 rsod-web Conda 环境"""
    # 1. 检查固定的 Miniconda 默认环境路径
    fixed_conda_path = r"C:\Users\Joe\miniconda3\envs\rsod-web\python.exe"
    if os.path.exists(fixed_conda_path):
        log_system(f"检测到指定的 Conda 环境 Python 解释器: {fixed_conda_path}")
        return fixed_conda_path
        
    # 2. 检查当前运行此脚本的 Python 是否已是虚拟环境
    if "rsod-web" in sys.prefix or os.environ.get("CONDA_DEFAULT_ENV") == "rsod-web":
        log_system(f"当前脚本运行在 rsod-web 虚拟环境中，使用: {sys.executable}")
        return sys.executable
        
    # 3. 检查系统 path 中是否有 conda 命令，尝试使用 conda run
    try:
        result = subprocess.run(["conda", "env", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
        if "rsod-web" in result.stdout:
            log_system("检测到本地 conda 环境 rsod-web，将采用 'conda run' 方式启动后端服务")
            return "conda_run"
    except FileNotFoundError:
        pass
        
    # 4. 保底方案，使用当前系统默认 python
    log_warn(f"未检测到 rsod-web 虚拟环境，使用当前系统默认解释器: {sys.executable}")
    return sys.executable

def stream_logs(pipe, prefix, color):
    """单线程循环读取输出流并打印"""
    try:
        # 逐行读取输出并添加前缀，使用 utf-8 解码兼容 Windows 中文日志
        for line in iter(pipe.readline, ''):
            if not line:
                break
            print(f"{color}{prefix}{COLOR_RESET} {line.rstrip()}")
    except Exception:
        pass

def kill_process_tree(proc):
    """强杀进程及其所有的子进程树，防止 Windows 平台下子进程残留占用端口"""
    pid = proc.pid
    if os.name == 'nt':
        log_system(f"正在强杀 Windows 进程树 (PID: {pid})...")
        try:
            # Windows 下通过 taskkill /T /F 强杀子进程树
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            log_error(f"清理 Windows 进程树失败: {e}")
    else:
        log_system(f"正在终止进程 (PID: {pid})...")
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        except Exception:
            pass

def clean_up_all():
    """程序退出时的统一资源回收"""
    log_system("正在关闭所有运行中的服务进程...")
    for proc in running_processes:
        kill_process_tree(proc)
    log_system("所有子服务进程清理完毕！")

def main():
    # 1. 端口预检
    if not check_ports():
        sys.exit(1)
        
    # 2. 启动 Docker 容器
    start_docker_services()
    
    # 3. 寻找 Python 环境
    python_interpreter = find_python_interpreter()
    
    # 4. 配置启动命令
    if python_interpreter == "conda_run":
        backend_cmd = ["conda", "run", "--no-capture-output", "-n", "rsod-web", "python", "main.py"]
    else:
        backend_cmd = [python_interpreter, "main.py"]
        
    # Windows 平台下 npm 需要使用 npm.cmd 执行
    if os.name == 'nt':
        frontend_cmd = ["npm.cmd", "run", "dev"]
    else:
        frontend_cmd = ["npm", "run", "dev"]
        
    log_system("正在启动后端服务 FastAPI...")
    try:
        # 启动后端子进程
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            bufsize=1,
            # Windows 下开启新的进程组，便于 Ctrl+C 时统一控制
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        running_processes.append(backend_proc)
    except Exception as e:
        log_error(f"后端服务启动失败: {e}")
        clean_up_all()
        sys.exit(1)
        
    log_system("正在启动前端服务 Vite/Vue...")
    try:
        # 启动前端子进程
        frontend_proc = subprocess.Popen(
            frontend_cmd,
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        running_processes.append(frontend_proc)
    except Exception as e:
        log_error(f"前端服务启动失败: {e}")
        clean_up_all()
        sys.exit(1)
        
    # 5. 使用守护线程流式传输日志
    t_backend = threading.Thread(
        target=stream_logs, 
        args=(backend_proc.stdout, "[Backend] ", COLOR_CYAN), 
        daemon=True
    )
    t_frontend = threading.Thread(
        target=stream_logs, 
        args=(frontend_proc.stdout, "[Frontend]", COLOR_YELLOW), 
        daemon=True
    )
    
    t_backend.start()
    t_frontend.start()
    
    log_system("==================================================================")
    log_system("  RSOD 遥感目标检测平台启动成功！")
    log_system(f"  - 后端 API 地址: http://localhost:{BACKEND_PORT}")
    log_system(f"  - 前端 Web 地址: http://localhost:{FRONTEND_PORT}")
    log_system("  - 提示: 终端正实时输出前后端日志，按 Ctrl+C 可一键关闭全部服务")
    log_system("==================================================================")
    
    # 6. 主进程循环监听，检查子进程生命状态
    try:
        while True:
            if backend_proc.poll() is not None:
                log_error(f"后端进程异常退出 (退出码: {backend_proc.returncode})")
                break
            if frontend_proc.poll() is not None:
                log_error(f"前端进程异常退出 (退出码: {frontend_proc.returncode})")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        # 捕获用户 Ctrl+C 信号
        print("") # 换行美化
        log_system("检测到 Ctrl+C 中断信号...")
    finally:
        # 统一清理所有服务
        clean_up_all()

if __name__ == "__main__":
    # 在 Windows 平台下激活 ANSI 颜色代码支持
    if os.name == 'nt':
        os.system('color')
    main()
