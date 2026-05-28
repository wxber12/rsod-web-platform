from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import datetime
import bcrypt
import traceback
from database import verify_user, get_db_connection
from app.utils.email_utils import send_reset_password_email
from app.config import settings
from psycopg2.extras import RealDictCursor

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str = None  # 允许注册时提供邮箱

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
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
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
        cursor.execute("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s);", (credentials.username, hashed, credentials.email, "user"))
        conn.commit()
        cursor.close(); conn.close()
        return {"code": 200, "message": "注册成功"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 500, "message": str(e)})

@router.get("/ping")
async def ping():
    return {"status": "ok", "message": "Auth router is working"}

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    print(f"DEBUG: 收到找回密码请求, email={request.email}")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # 使用填写的邮箱去数据库中查找对应的用户（不区分大小写）
        cursor.execute("SELECT id, username, email FROM users WHERE LOWER(email) = LOWER(%s);", (request.email.strip(),))
        user = cursor.fetchone()
        
        if not user:
            print(f"DEBUG: 数据库中未找到该邮箱: {request.email}")
            return JSONResponse(
                status_code=404, 
                content={"code": 404, "message": "该邮箱尚未注册，请检查输入或先前往注册"}
            )
            
        if not user["email"]:
            print(f"DEBUG: 用户 {user['username']} 存在但邮箱字段为空")
            return JSONResponse(
                status_code=400, 
                content={"code": 400, "message": "该用户未绑定邮箱，无法通过邮箱找回"}
            )
            
        user_id = user["id"]
        print(f"DEBUG: 找到用户 ID={user_id}, 准备发送邮件")
        
        # 生成重置 Token
        token_payload = {
            "user_id": user_id, 
            "action": "reset-password", 
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }
        reset_token = jwt.encode(token_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        
        # 拼接前端的重置密码页面链接
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        # 发送真实邮件给该用户的邮箱
        success, error_msg = send_reset_password_email(user["email"], reset_link)
        
        if success:
            print(f"DEBUG: 邮件发送成功!")
            return {"code": 200, "message": "重置链接已成功发送到您的邮箱，请查收！", "token": reset_token}
        else:
            print(f"DEBUG: 邮件发送失败: {error_msg}")
            return JSONResponse(status_code=500, content={"code": 500, "message": f"邮件发送失败: {error_msg}"})
            
    except Exception as e:
        print(f"DEBUG: 找回密码逻辑出现异常: {str(e)}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"code": 500, "message": f"系统错误: {str(e)}"})
    finally:
        cursor.close()
        conn.close()

@router.post("/reset-password")
async def reset_password(request_data: ResetPasswordRequest):
    try:
        payload = jwt.decode(request_data.token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
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