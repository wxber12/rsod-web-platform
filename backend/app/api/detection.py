import os
from typing import List
from app.api.profile import get_current_user
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.services.detection_service import detection_service
from app.utils.file_utils import save_upload_file, ensure_directories
from app.config import settings
from app.models.schemas import SingleDetectionResponse, BatchDetectionResponse, VideoDetectionResponse, TargetListResponse

router = APIRouter(prefix="/detection", tags=["detection"])

ensure_directories()


@router.post("/single", response_model=SingleDetectionResponse)
async def detect_single_image(
        file: UploadFile = File(...),
        model_name: str = Form("pest-v1"),
        current_user: dict = Depends(get_current_user)
):
    try:
        filename = await save_upload_file(file, settings.UPLOAD_DIR)
        image_path = os.path.join(settings.UPLOAD_DIR, filename)

        result = detection_service.detect_single_image(image_path, model_name, user_id=current_user["user_id"])

        return SingleDetectionResponse(
            success=True,
            message="检测成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")


@router.post("/batch", response_model=BatchDetectionResponse)
async def detect_batch(
        files: List[UploadFile] = File(...),
        model_name: str = Form("best"),
        current_user: dict = Depends(get_current_user)
):
    try:
        image_paths = []
        for file in files:
            filename = await save_upload_file(file, settings.UPLOAD_DIR)
            image_path = os.path.join(settings.UPLOAD_DIR, filename)
            image_paths.append(image_path)

        results = detection_service.detect_batch_images(image_paths, model_name, user_id=current_user["user_id"])

        return BatchDetectionResponse(
            success=True,
            message=f"成功检测 {len(results)} 张图片",
            data=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量检测失败: {str(e)}")


@router.post("/video", response_model=VideoDetectionResponse)
async def detect_video(
        file: UploadFile = File(...),
        model_name: str = Form("best"),
        current_user: dict = Depends(get_current_user)
):
    try:
        filename = await save_upload_file(file, settings.UPLOAD_DIR)
        video_path = os.path.join(settings.UPLOAD_DIR, filename)

        result = detection_service.detect_video(video_path, model_name, user_id=current_user["user_id"])

        return VideoDetectionResponse(
            success=True,
            message="视频检测成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频检测失败: {str(e)}")


@router.get("/targets/list", response_model=TargetListResponse)
async def get_targets():
    """获取目标库列表"""
    targets = [
        {"id": 1, "name": "飞机", "count": 1250, "icon": "Plane"},
        {"id": 2, "name": "油罐", "count": 840, "icon": "Oiltank"},
        {"id": 3, "name": "立交桥", "count": 420, "icon": "Overpass"},
        {"id": 4, "name": "操场", "count": 310, "icon": "Playground"}
    ]
    return TargetListResponse(
        success=True,
        message="获取成功",
        data=targets
    )