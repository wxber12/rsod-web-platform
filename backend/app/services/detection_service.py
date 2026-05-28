import os
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
from app.utils.minio_utils import storage
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
        print(f"DEBUG: 尝试加载模型文件: {model_path}")

        if model_path.exists():
            print(f"DEBUG: 正在加载新模型: {model_path} ...")
            try:
                # YOLO 加载路径建议转为字符串
                model = YOLO(str(model_path))
                self.models[model_name] = model

                if hasattr(model, 'names'):
                    self.class_names[model_name] = model.names
                else:
                    self.class_names[model_name] = {0: "target"}

                print(f"DEBUG: 模型 {model_name} 加载成功")
                return model
            except Exception as e:
                print(f"DEBUG: 模型加载失败: {str(e)}")
                raise e
        else:
            print(f"DEBUG: 模型文件不存在: {model_path}")
            raise FileNotFoundError(f"找不到模型文件: {model_path}，请检查是否已放入该目录！")

    def detect_single_image(self, image_path: str, model_name: str = "best", user_id: int = None) -> DetectionResult:
        """单张图片检测逻辑，支持检测 (detect) 和分类 (classify) 模型"""
        start_time = time.time()
        detection_id = str(uuid.uuid4())
        model = self._get_or_load_model(model_name)

        # 运行推理
        results = model.predict(
            source=image_path,
            conf=settings.CONFIDENCE_THRESHOLD if model.task == 'detect' else 0.1,
            save=False
        )

        boxes = []
        
        # 🌟 核心适配逻辑：根据模型任务类型处理结果
        if model.task == 'classify':
            # 分类模型：获取置信度最高的一个类别
            probs = results[0].probs
            top1_idx = probs.top1
            conf = float(probs.top1conf)
            class_name = model.names[top1_idx]
            chinese_name = self.get_class_chinese_name(class_name)
            
            # 为分类结果生成一个“全图虚拟框”，方便前端展示标签
            # 假设图片尺寸 (通常分类模型推理不关心具体坐标，我们给个 0,0,100,100)
            boxes.append(DetectionBox(
                x1=0, y1=0, x2=0, y2=0, # 坐标设为0，前端不画框但显示标签
                confidence=conf,
                class_id=top1_idx,
                class_name=class_name,
                chinese_name=chinese_name
            ))
        else:
            # 检测模型：原有画框逻辑
            if results[0].boxes:
                for box in results[0].boxes:
                    b = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    class_name = model.names[cls_id]
                    chinese_name = self.get_class_chinese_name(class_name)
                    
                    boxes.append(DetectionBox(
                        x1=b[0], y1=b[1], x2=b[2], y2=b[3],
                        confidence=conf,
                        class_id=cls_id,
                        class_name=class_name,
                        chinese_name=chinese_name
                    ))

        # 过滤置信度为 0 的框 (用户反馈不希望看到 0% 的结果)
        boxes = [box for box in boxes if box.confidence > 0]

        # 1. 上传原始图片到 MinIO
        original_filename = f"uploads/{detection_id}_{Path(image_path).name}"
        original_url = storage.upload_local_file(image_path, original_filename)

        # 2. 生成并上传结果图片到 MinIO
        # 对于 last 模型，绘图时不显示置信度 (用户反馈图片上的置信度太乱)
        plot_conf = False if model_name == 'last' else True
        annotated_image = results[0].plot(conf=plot_conf)
        
        temp_result_path = os.path.join(settings.RESULT_DIR, f"temp_res_{detection_id}.jpg")
        cv2.imwrite(temp_result_path, annotated_image)
        
        result_filename = f"results/{detection_id}_res.jpg"
        result_url = storage.upload_local_file(temp_result_path, result_filename)
        
        # 删除临时结果文件
        if os.path.exists(temp_result_path):
            os.remove(temp_result_path)

        res = DetectionResult(
            detection_id=detection_id,
            image_url=original_url,
            result_image_url=result_url,
            boxes=boxes,
            total_objects=len(boxes),
            detection_time=round(time.time() - start_time, 3),
            model_name=model_name,
            created_at=datetime.now()
        )

        # 保存历史记录 (关联 user_id)
        self.save_history(
            user_id=user_id,
            detection_id=res.detection_id,
            type="single",
            original_url=res.image_url,
            result_url=res.result_image_url,
            total_objects=res.total_objects,
            detection_time=res.detection_time,
            model_name=res.model_name
        )

        return res

    def detect_batch_images(self, image_paths: List[str], model_name: str = "best", user_id: int = None) -> List[DetectionResult]:
        """批量检测多张图片"""
        results_list = []
        for path in image_paths:
            try:
                # 简单复用单图逻辑，后续可根据性能需求优化为真正的 Batch 推理
                res = self.detect_single_image(path, model_name, user_id=user_id)
                results_list.append(res)
            except Exception as e:
                print(f"批量检测中单张图片处理失败: {path}, error: {e}")
                continue
        return results_list

    def detect_video(self, video_path: str, model_name: str = "best", user_id: int = None) -> VideoDetectionResult:
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
        
        # 1. 上传原始视频到 MinIO
        original_filename = f"uploads/{detection_id}_{Path(video_path).name}"
        original_url = storage.upload_local_file(video_path, original_filename)

        # 临时存储本地处理后的视频
        temp_result_filename = os.path.join(settings.RESULT_DIR, f"temp_res_{detection_id}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') # 临时用 mp4v，后续 FFmpeg 转码更稳
        out = cv2.VideoWriter(temp_result_filename, fourcc, fps, (width, height))

        frame_count = 0
        total_objects_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 运行推理
            results = model.predict(
                source=frame,
                conf=settings.CONFIDENCE_THRESHOLD if model.task == 'detect' else 0.1,
                save=False,
                verbose=False
            )
            
            # 统计当前帧目标数
            if model.task == 'classify':
                total_objects_count += 1 # 分类模型每帧算1个目标
            else:
                total_objects_count += len(results[0].boxes) if results[0].boxes else 0
            
            # 绘制结果并写入视频
            # 对于 last 模型，绘图时不显示置信度
            plot_conf = False if model_name == 'last' else True
            annotated_frame = results[0].plot(conf=plot_conf)
            out.write(annotated_frame)
            frame_count += 1

        cap.release()
        out.release()

        # 2. 上传结果视频到 MinIO
        result_filename = f"results/{detection_id}_res.mp4"
        result_url = storage.upload_local_file(temp_result_filename, result_filename)
        
        # 删除本地临时视频
        if os.path.exists(temp_result_filename):
            os.remove(temp_result_filename)

        res = VideoDetectionResult(
            detection_id=detection_id,
            video_url=original_url,
            result_video_url=result_url,
            total_frames=frame_count,
            total_objects=total_objects_count,
            detection_time=round(time.time() - start_time, 3),
            model_name=model_name,
            created_at=datetime.now()
        )
        
        # 保存历史记录 (关联 user_id)
        self.save_history(
            user_id=user_id,
            detection_id=res.detection_id,
            type="video",
            original_url=res.video_url,
            result_url=res.result_video_url,
            total_objects=res.total_objects,
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

    def get_class_chinese_name(self, class_name: str) -> str:
        """获取类别的中文名称，增强对不同模型类别的兼容性"""
        mapping = {
            "aircraft": "飞机",
            "oiltank": "油罐",
            "overpass": "立交桥",
            "playground": "操场",
            "car": "小汽车",
            "truck": "卡车",
            "vehicle": "车辆",
            "ship": "船舶",
            "building": "建筑物",
            # PlantVillage 常见类别映射
            "apple": "苹果",
            "corn": "玉米",
            "grape": "葡萄",
            "potato": "土豆",
            "tomato": "番茄",
            "healthy": "健康",
            "leaf": "叶片"
        }
        
        lower_name = class_name.lower()
        # 1. 优先完全匹配
        if lower_name in mapping:
            return mapping[lower_name]
            
        # 2. 处理 PlantVillage 风格名称 (如 Apple___Apple_scab)
        if "___" in class_name:
            parts = class_name.split("___")
            plant = mapping.get(parts[0].lower(), parts[0])
            disease = parts[1].replace("_", " ")
            return f"{plant} - {disease}"
            
        # 3. 模糊匹配映射表中的关键词
        for key, value in mapping.items():
            if key in lower_name:
                return value
                
        return class_name

# 单例模式导出服务对象
detection_service = DetectionService()