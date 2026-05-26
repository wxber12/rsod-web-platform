import base64
import cv2
import numpy as np
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.services.camera_detection_service import camera_detection_service
from app.api.profile import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/camera", tags=["camera"])

@router.post("/detect")
async def detect_frame(request: dict, current_user: dict = Depends(get_current_user)):
    """
    接收前端发送的图像并返回检测结果
    """
    try:
        if not camera_detection_service.is_running:
            return {"success": False, "message": "摄像头检测未启动"}
            
        # 获取图像数据
        image_data = request.get("image")
        if not image_data:
            return {"success": False, "message": "缺少图像数据"}
            
        # 解码 Base64 图像
        if "," in image_data:
            image_data = image_data.split(",")[1]
            
        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"success": False, "message": "图像解码失败"}
            
        # 调用检测服务
        result = camera_detection_service.detect_image(image)
        
        return {
            "success": True,
            "message": "检测成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"图像检测异常: {str(e)}")
        return {"success": False, "message": f"图像检测失败: {str(e)}"}
