from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.detection import router as detection_router # 导入 detection.py 中的 router
from app.api.ai import router as ai_router
from app.api.history import router as history_router
from app.api.profile import router as profile_router
import os
from app.utils.paths import Paths
from app.config import settings
# 在应用启动时自动检查并创建必要的目录结构
Paths.init_all_dirs()

app = FastAPI()

os.makedirs("static", exist_ok=True)
os.makedirs("runs", exist_ok=True)
app.mount("/runs", StaticFiles(directory="runs"), name="runs")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由，前缀会自动拼接 (例如: /api/auth/login)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(detection_router, prefix="/api", tags=["detection"])
app.include_router(ai_router, prefix="/api", tags=["ai"])
app.include_router(history_router, prefix="/api", tags=["history"])
app.include_router(profile_router, prefix="/api", tags=["profile"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)