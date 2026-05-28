import time
import threading
import logging
import uuid
import cv2
import io
from datetime import datetime
from typing import Dict, Any, Optional
import numpy as np
from app.services.detection_service import detection_service
from app.config import settings
from app.utils.minio_utils import storage

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
        
        # 历史记录节流：每个用户每 10 秒最多保存一次
        self._last_save_time = {} # {user_id: timestamp}
        
        # 配置
        self._confidence_threshold = 0.15 # 🌟 再次降低阈值，确保远距离小目标也能被捕捉
        self._iou_threshold = 0.45 # 🌟 恢复标准 IOU 阈值，防止框重叠过滤严重
        self._model_image_size = 640
        
        # 并发控制
        self._max_concurrent_requests = 5
        self._request_semaphore = threading.Semaphore(self._max_concurrent_requests)
        
        self._initialized = True

    def detect_image(self, image: np.ndarray, user_id: int = None, model_name: str = "best") -> Dict[str, Any]:
        """
        检测单张图像（核心推理方法）
        
        参数：
            image: 输入图像（BGR格式）
            user_id: 当前用户ID
            model_name: 使用的模型名称
            
        返回：
            Dict: 检测结果
        """
        with self._request_semaphore:
            start_time = time.time()
            
            # 确保模型已加载
            model = detection_service._get_or_load_model(model_name)
            
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
            
            if model.task == 'classify':
                # 🌟 适配分类模型
                probs = results[0].probs
                top1_idx = probs.top1
                conf = float(probs.top1conf)
                class_name = model.names[top1_idx]
                chinese_name = detection_service.get_class_chinese_name(class_name)
                
                boxes.append({
                    "x1": 0, "y1": 0, "x2": 0, "y2": 0,
                    "confidence": conf,
                    "class_id": top1_idx,
                    "class_name": class_name,
                    "chinese_name": chinese_name
                })
            else:
                # 🌟 适配检测模型
                for result in results:
                    if result.boxes:
                        for box in result.boxes:
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            confidence = float(box.conf[0])
                            class_id = int(box.cls[0])
                            class_name = model.names[class_id]
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
            
            # 过滤置信度为 0 的结果 (用户反馈不希望显示 0% 置信度目标)
            boxes = [box for box in boxes if box["confidence"] > 0]
            
            # --- 历史记录自动保存逻辑 (节流控制) ---
            current_time = time.time()
            if user_id and len(boxes) > 0:
                last_save = self._last_save_time.get(user_id, 0)
                if current_time - last_save > 10: # 10秒保存一次有目标的快照
                    self._last_save_time[user_id] = current_time
                    threading.Thread(target=self._async_save_history, args=(image, results[0], boxes, user_id, detection_time, model_name)).start()
            
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

    def _async_save_history(self, image, result, boxes, user_id, detection_time, model_name):
        """异步保存摄像头快照到历史记录"""
        try:
            detection_id = f"cam_{uuid.uuid4().hex[:8]}"
            
            # 1. 上传原始快照
            _, buffer = cv2.imencode('.jpg', image)
            original_url = storage.client.put_object(
                storage.bucket_name,
                f"uploads/{detection_id}_orig.jpg",
                io.BytesIO(buffer),
                length=len(buffer),
                content_type="image/jpeg"
            )
            original_url = storage.get_url(f"uploads/{detection_id}_orig.jpg")

            # 2. 上传带框结果
            # 对于 last 模型，绘图时不显示置信度
            plot_conf = False if model_name == 'last' else True
            annotated_image = result.plot(conf=plot_conf)
            _, buffer_res = cv2.imencode('.jpg', annotated_image)
            result_url = storage.client.put_object(
                storage.bucket_name,
                f"results/{detection_id}_res.jpg",
                io.BytesIO(buffer_res),
                length=len(buffer_res),
                content_type="image/jpeg"
            )
            result_url = storage.get_url(f"results/{detection_id}_res.jpg")

            # 3. 写入数据库
            detection_service.save_history(
                user_id=user_id,
                detection_id=detection_id,
                type="camera",
                original_url=original_url,
                result_url=result_url,
                total_objects=len(boxes),
                detection_time=round(detection_time, 3),
                model_name=model_name
            )
            logger.info(f"📸 摄像头快照已自动保存到历史: {detection_id}")
        except Exception as e:
            logger.error(f"❌ 摄像头快照保存失败: {e}")

camera_detection_service = CameraDetectionService()
