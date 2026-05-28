from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import time
from app.api.auth import router as auth_router
from app.api.detection import router as detection_router # 导入 detection.py 中的 router
from app.api.ai import router as ai_router
from app.api.history import router as history_router
from app.api.profile import router as profile_router
from app.api.camera import router as camera_router
import os
from app.utils.paths import Paths
# 在应用启动时自动检查并创建必要的目录结构
Paths.init_all_dirs()

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    print(f"DEBUG: {request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)")
    return response

os.makedirs("static", exist_ok=True)
os.makedirs("runs", exist_ok=True)
app.mount("/runs", StaticFiles(directory="runs"), name="runs")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
app.include_router(camera_router, prefix="/api", tags=["camera"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)