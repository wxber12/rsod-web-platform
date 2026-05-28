from fastapi import APIRouter, Depends, HTTPException, Header
import jwt
from app.config import settings
from database import get_db_connection
from psycopg2.extras import RealDictCursor
from app.models.schemas import UserProfile, UpdateProfileRequest, ChangePasswordRequest
import bcrypt

router = APIRouter(prefix="/profile", tags=["profile"])

async def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="未授权或登录已过期")

@router.get("/", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT id, username, email, role, avatar, created_at FROM users WHERE id = %s", (current_user["user_id"],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.put("/")
async def update_profile(request: UpdateProfileRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.email:
        cursor.execute("UPDATE users SET email = %s WHERE id = %s", (request.email, current_user["user_id"]))
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True, "message": "资料更新成功"}

@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT password FROM users WHERE id = %s", (current_user["user_id"],))
    user = cursor.fetchone()
    
    if not user or not bcrypt.checkpw(request.old_password.encode('utf-8'), user['password'].encode('utf-8')):
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="原密码错误")
    
    hashed = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, current_user["user_id"]))
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True, "message": "密码修改成功"}
