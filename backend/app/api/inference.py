from fastapi import APIRouter, UploadFile, File
import os, uuid
from ultralytics import YOLO

router = APIRouter()
model = YOLO("yolo11n.pt")


@router.post("/single")
async def inference_single(file: UploadFile = File(...)):
    temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
    temp_path = os.path.join("static", temp_filename)
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    results = model(temp_path, save=True, project="runs/detect", name="latest", exist_ok=True)
    relative_img_path = os.path.relpath(os.path.join(results[0].save_dir, temp_filename), os.getcwd())

    return {
        "code": 200,
        "data": {
            "image_url": f"http://localhost:8000/{relative_img_path}",
            "detections": [{"class": model.names[int(b.cls[0])], "confidence": float(b.conf[0])} for b in
                           results[0].boxes]
        }
    }