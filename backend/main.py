from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.inference import router as inference_router
import os

app = FastAPI()

os.makedirs("static", exist_ok=True)
os.makedirs("runs", exist_ok=True)
app.mount("/runs", StaticFiles(directory="runs"), name="runs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由，前缀会自动拼接 (例如: /api/auth/login)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(inference_router, prefix="/api/inference", tags=["inference"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)