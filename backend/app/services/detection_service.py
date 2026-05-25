import time
import uuid
import cv2
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from ultralytics import YOLO

# 从你的工程基础设施中导入
from app.config import settings
from app.models.schemas import DetectionBox, DetectionResult, VideoDetectionResult
from app.utils.file_utils import get_file_url
from database import get_db_connection
from app.utils.paths import Paths  # 核心：使用统一的路径管理类

class DetectionService:
    def __init__(self):
        # 使用字典缓存已加载的模型
        self.models: Dict[str, YOLO] = {}
        self.class_names: Dict[str, dict] = {}

        # 【工程化修改】：通过 Paths 类获取路径，彻底告别硬编码
        self.models_dir = Paths.models()

    def _get_or_load_model(self, model_name: str) -> YOLO:
        """根据前端传来的名字，动态加载对应的模型"""
        if model_name in self.models:
            return self.models[model_name]

        # 【工程化修改】：使用 Path 对象拼接，自动处理分隔符
        model_path = self.models_dir / f"{model_name}.pt"

        if model_path.exists():
            print(f"正在加载新模型: {model_path} ...")
            # YOLO 加载路径建议转为字符串
            model = YOLO(str(model_path))
            self.models[model_name] = model

            if hasattr(model, 'names'):
                self.class_names[model_name] = model.names
            else:
                self.class_names[model_name] = {0: "target"}

            return model
        else:
            raise FileNotFoundError(f"找不到模型文件: {model_path}，请检查是否已放入该目录！")

    def detect_single_image(self, image_path: str, model_name: str = "best") -> DetectionResult:
        start_time = time.time()
        detection_id = str(uuid.uuid4())

        model = self._get_or_load_model(model_name)
        current_class_names = self.class_names.get(model_name, {})

        results = model.predict(
            source=image_path,
            conf=settings.CONFIDENCE_THRESHOLD,
            iou=settings.IOU_THRESHOLD,
            save=False
        )

        boxes = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                class_id = int(box.cls[0])
                boxes.append(DetectionBox(
                    x1=x1, y1=y1, x2=x2, y2=y2,
                    confidence=float(box.conf[0]),
                    class_id=class_id,
                    class_name=current_class_names.get(class_id, f"class_{class_id}")
                ))

        # 【工程化修改】：确保结果目录存在，并使用 Path 操作
        result_dir = Paths.ensure_dir(Path(settings.RESULT_DIR))
        result_filename = f"result_{uuid.uuid4().hex}.jpg"
        result_path = result_dir / result_filename

        annotated_image = results[0].plot()
        cv2.imwrite(str(result_path), annotated_image)

        res = DetectionResult(
            detection_id=detection_id,
            image_url=get_file_url(Path(image_path).name, settings.UPLOAD_DIR),
            result_image_url=get_file_url(result_filename, settings.RESULT_DIR),
            boxes=boxes,
            total_objects=len(boxes),
            detection_time=round(time.time() - start_time, 3),
            model_name=model_name,
            created_at=datetime.now()
        )

        # 保存历史记录
        self.save_history(
            user_id=None,
            detection_id=res.detection_id,
            type="single",
            original_url=res.image_url,
            result_url=res.result_image_url,
            total_objects=res.total_objects,
            detection_time=res.detection_time,
            model_name=res.model_name
        )

        return res

    def detect_batch_images(self, image_paths: List[str], model_name: str = "best") -> List[DetectionResult]:
        """批量检测多张图片"""
        results_list = []
        for path in image_paths:
            try:
                # 简单复用单图逻辑，后续可根据性能需求优化为真正的 Batch 推理
                res = self.detect_single_image(path, model_name)
                results_list.append(res)
            except Exception as e:
                print(f"批量检测中单张图片处理失败: {path}, error: {e}")
                continue
        return results_list

    def detect_video(self, video_path: str, model_name: str = "best") -> VideoDetectionResult:
        """视频检测逻辑"""
        start_time = time.time()
        detection_id = str(uuid.uuid4())
        model = self._get_or_load_model(model_name)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("无法打开视频文件")

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        result_dir = Paths.ensure_dir(Path(settings.RESULT_DIR))
        result_filename = f"result_{uuid.uuid4().hex}.mp4"
        result_path = result_dir / result_filename

        # 使用 avc1 (H.264) 编码以支持浏览器播放
        # 如果系统环境不支持 avc1，可以退回到 mp4v
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(str(result_path), fourcc, fps, (width, height))
        
        # 如果 avc1 失败，尝试 mp4v
        if not out.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(result_path), fourcc, fps, (width, height))

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 运行推理
            results = model.predict(
                source=frame,
                conf=settings.CONFIDENCE_THRESHOLD,
                iou=settings.IOU_THRESHOLD,
                save=False,
                verbose=False
            )
            
            # 绘制结果并写入视频
            annotated_frame = results[0].plot()
            out.write(annotated_frame)
            frame_count += 1

        cap.release()
        out.release()

        res = VideoDetectionResult(
            detection_id=detection_id,
            video_url=get_file_url(Path(video_path).name, settings.UPLOAD_DIR),
            result_video_url=get_file_url(result_filename, settings.RESULT_DIR),
            total_frames=frame_count,
            detection_time=round(time.time() - start_time, 3),
            model_name=model_name,
            created_at=datetime.now()
        )
        
        # 保存历史记录
        self.save_history(
            user_id=None, # 后续从 API 层传入
            detection_id=res.detection_id,
            type="video",
            original_url=res.video_url,
            result_url=res.result_video_url,
            total_objects=0, # 视频暂不统计总数
            detection_time=res.detection_time,
            model_name=res.model_name
        )
        
        return res

    def save_history(self, user_id, detection_id, type, original_url, result_url, total_objects, detection_time, model_name):
        """保存检测历史到数据库"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO detection_history 
                (user_id, detection_id, type, original_url, result_url, total_objects, detection_time, model_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, detection_id, type, original_url, result_url, total_objects, detection_time, model_name))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"✅ 历史记录已保存: {detection_id}")
        except Exception as e:
            print(f"❌ 历史记录保存失败: {e}")

# 单例模式导出服务对象
detection_service = DetectionService()