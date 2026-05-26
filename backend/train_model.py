import os
import argparse
from ultralytics import YOLO
from datetime import datetime
import json
import shutil


# 【已注释】如果本地没有配置 MinIO 环境，无需导入此服务
# from app.services.minio_service import minio_service

class YOLOTrainer:
    def __init__(self, model_name="yolo11n.pt"):
        self.model = YOLO(model_name)
        self.base_model_name = "rsod-yolo11n"

    def train(self, data_yaml, epochs=100, batch=16, imgsz=640, device='cpu', version=None):
        """执行训练、评估"""
        # 1. 执行 YOLO 训练
        results = self.model.train(data=data_yaml, epochs=epochs, batch=batch, imgsz=imgsz, device=device)

        # 2. 获取最佳模型路径（YOLO 训练完成后会自动保存在 runs 目录）
        best_pt = self.model.trainer.best
        print(f"✅ 训练完成！最佳模型已保存至: {best_pt}")

        # 3. 如果你需要本地元数据记录，可以保留这部分逻辑
        version = version or f"v1.0.0"
        metadata = {
            "name": self.base_model_name,
            "version": version,
            "created_at": datetime.now().isoformat(),
            "metrics": {
                "mAP50": float(results.box.map50),
                "mAP50-95": float(results.box.map),
                "precision": float(results.box.p.mean()),
                "recall": float(results.box.r.mean())
            },
            "config": {"epochs": epochs, "batch": batch, "imgsz": imgsz, "device": device}
        }

        # 【已注释】跳过 MinIO 上传逻辑
        # object_name = f"{self.base_model_name}-best_{version}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pt"
        # minio_service.upload_model(best_pt, object_name, metadata)
        # print(f"✅ 模型上传成功！URL: {minio_service.get_url(object_name)}")

        print("💡 提示：MinIO 上传已跳过，您可以直接使用本地生成的 best.pt 进行部署。")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch', type=int, default=16)
    parser.add_argument('--device', type=str, default='cpu')
    parser.add_argument('--version', type=str, default=None)
    args = parser.parse_args()

    # 确保路径指向你转换好的 yaml 文件
    yaml_path = os.path.join("data", "rsod", "yolo_dataset", "rsod.yaml")

    trainer = YOLOTrainer()
    trainer.train(data_yaml=yaml_path,
                  epochs=args.epochs,
                  batch=args.batch,
                  device=args.device,
                  version=args.version)


if __name__ == "__main__":
    main()