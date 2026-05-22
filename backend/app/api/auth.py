from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import datetime
import bcrypt
import traceback
from database import verify_user, get_db_connection

router = APIRouter()

# 保持与 main.py 一致的密钥
JWT_SECRET = "rsod-platform-secret-key-2026-secure-xyz"
JWT_ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/login")
async def login(credentials: LoginRequest):
    user_info = verify_user(credentials.username, credentials.password)
    if user_info:
        now = datetime.datetime.utcnow()
        payload = {
            "user_id": user_info["id"],
            "username": user_info["username"],
            "role": user_info["role"],
            "exp": int((now + datetime.timedelta(hours=24)).timestamp()),
            "iat": int(now.timestamp())
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return {"code": 200, "message": "登录成功", "data": {"token": token, "user": {"username": user_info["username"], "role": user_info["role"]}}}
    return JSONResponse(status_code=400, content={"code": 400, "message": "用户名或密码错误！"})

@router.post("/register")
async def register(credentials: RegisterRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s;", (credentials.username,))
        if cursor.fetchone():
            return JSONResponse(status_code=400, content={"code": 400, "message": "用户名已存在"})

        hashed = bcrypt.hashpw(credentials.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s);", (credentials.username, hashed, "user"))
        conn.commit()
        cursor.close(); conn.close()
        return {"code": 200, "message": "注册成功"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 500, "message": str(e)})

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    # 模拟生成逻辑
    token_payload = {"user_id": 1, "action": "reset-password", "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}
    reset_token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"code": 200, "message": "链接已发送", "token": reset_token}

@router.post("/reset-password")
async def reset_password(request_data: ResetPasswordRequest):
    try:
        payload = jwt.decode(request_data.token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("action") != "reset-password":
            return JSONResponse(status_code=400, content={"code": 400, "message": "无效链接"})

        hashed = bcrypt.hashpw(request_data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE id = %s;", (hashed, payload["user_id"]))
        conn.commit()
        cursor.close(); conn.close()
        return {"code": 200, "message": "密码修改成功"}
    except Exception as e:
        return JSONResponse(status_code=400, content={"code": 400, "message": "无效或过期链接"})