import os
import uuid
import traceback
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

app = FastAPI()

# 确保必要的临时目录存在
os.makedirs("static", exist_ok=True)
os.makedirs("runs", exist_ok=True)

# 直接挂载最外层的 runs 文件夹
app.mount("/runs", StaticFiles(directory="runs"), name="runs")

# 加载 YOLO 模型
model = YOLO("yolo11n.pt")

# 允许 Vue 前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 测试连接接口
@app.get("/api/test/connect")
async def test_connect():
    return {"code": 200, "message": "前后端连通成功！"}


# 核心推理接口
@app.post("/api/inference/single")
async def inference_single(file: UploadFile = File(...)):
    try:
        # 1. 保存临时文件
        temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join("static", temp_filename)

        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # 2. YOLO 推理
        results = model(
            temp_path,
            save=True,
            project="runs/detect",
            name="latest",
            exist_ok=True
        )

        # 🔥【核心大招】：直接问 YOLO 它把图片存到哪个绝对路径文件夹了！
        yolo_save_dir = results[0].save_dir

        # 3. 动态获取标注图片的绝对路径
        absolute_result_path = os.path.join(yolo_save_dir, temp_filename)

        if not os.path.exists(absolute_result_path):
            raise Exception(f"结果图片未生成: {absolute_result_path}")

        # 4. 把绝对路径转换成相对于项目根目录的相对路径（方便前端通过挂载的 /runs 访问）
        # 比如把 /Users/.../backend/runs/detect/runs/latest/temp.jpg 变成 runs/detect/runs/latest/temp.jpg
        project_root = os.getcwd()
        relative_img_path = os.path.relpath(absolute_result_path, project_root)

        # 生成可访问的 URL
        result_img_url = f"http://localhost:8000/{relative_img_path}"

        # 5. 解析检测结果
        detections = []
        for box in results[0].boxes:
            detections.append({
                "class": model.names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "bbox": box.xyxy[0].tolist()
            })

        # 6. 清理临时原文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            "code": 200,
            "message": "推理成功",
            "data": {
                "detections": detections,
                "image_url": result_img_url
            }
        }

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": f"推理失败: {str(e)}"}
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)