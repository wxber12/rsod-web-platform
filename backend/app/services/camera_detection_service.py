import time
import threading
import logging
from typing import Dict, Any, Optional
import numpy as np
from app.services.detection_service import detection_service
from app.config import settings

logger = logging.getLogger(__name__)

class CameraDetectionService:
    _instance: Optional['CameraDetectionService'] = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # 检测状态
        self.is_running = True
        
        # 统计信息
        self._frame_count = 0
        self._fps_frame_count = 0
        self._last_fps_time = time.time()
        
        # 配置
        self._confidence_threshold = 0.5
        self._iou_threshold = 0.7
        self._model_image_size = 320  # 降低分辨率提升速度
        
        # 并发控制
        self._max_concurrent_requests = 5
        self._request_semaphore = threading.Semaphore(self._max_concurrent_requests)
        
        self._initialized = True

    def detect_image(self, image: np.ndarray) -> Dict[str, Any]:
        """
        检测单张图像（核心推理方法）
        
        参数：
            image: 输入图像（BGR格式）
            
        返回：
            Dict: 检测结果
        """
        with self._request_semaphore:
            start_time = time.time()
            
            # 确保模型已加载
            model = detection_service._get_or_load_model("best")
            
            # 调用 YOLO 模型进行预测
            results = model.predict(
                source=image,
                conf=self._confidence_threshold,
                iou=self._iou_threshold,
                save=False,
                imgsz=self._model_image_size,
                half=False,
                verbose=False,
                stream=False
            )
            
            # 解析检测结果
            boxes = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = model.names[cls_id]
                    chinese_name = detection_service.get_class_chinese_name(class_name)
                    
                    boxes.append({
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                        "confidence": confidence,
                        "class_id": class_id,
                        "class_name": class_name,
                        "chinese_name": chinese_name
                    })
            
            detection_time = time.time() - start_time
            
            # 更新统计信息
            self._frame_count += 1
            self._fps_frame_count += 1
            current_time = time.time()
            elapsed = current_time - self._last_fps_time
            
            fps = 0.0
            if elapsed >= 1.0:
                fps = self._fps_frame_count / elapsed
                self._fps_frame_count = 0
                self._last_fps_time = current_time
                
            return {
                "boxes": boxes,
                "frame_index": self._frame_count,
                "fps": round(fps, 1),
                "detection_time": round(detection_time, 3),
                "total_objects": len(boxes)
            }

camera_detection_service = CameraDetectionService()
