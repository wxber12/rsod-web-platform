"""
YOLO11 病虫害分类模型训练脚本
用法：python scripts/train.py [--model yolo11n-cls] [--epochs 50] [--batch 32]
"""

import argparse
import json
import shutil
import time
from pathlib import Path

# ============================================================
# 路径配置
# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATASET_DIR  = PROJECT_ROOT / "dataset"
MODELS_DIR   = PROJECT_ROOT / "backend" / "models"
RUNS_DIR     = PROJECT_ROOT / "backend" / "runs" / "classify"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
RUNS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 训练
# ============================================================

def train(model_name: str, epochs: int, batch: int, patience: int):
    from ultralytics import YOLO
    import torch

    device = "0" if torch.cuda.is_available() else "cpu"
    print(f"[train] 设备: {'GPU ' + torch.cuda.get_device_name(0) if device == '0' else 'CPU'}")
    print(f"[train] 模型: {model_name}  epochs={epochs}  batch={batch}  patience={patience}")
    print(f"[train] 数据集: {DATASET_DIR}  (train/val/test 均已就绪)")

    model = YOLO(f"{model_name}.pt")  # 自动下载预训练权重

    results = model.train(
        data=str(DATASET_DIR),   # YOLO11 分类任务直接传目录
        epochs=epochs,
        imgsz=224,
        batch=batch,
        patience=patience,       # 早停：连续 N 轮无提升则停止
        device=device,
        project=str(RUNS_DIR),
        name="plant_disease",
        exist_ok=True,
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,                # 最终学习率 = lr0 * lrf
        weight_decay=0.0005,
        warmup_epochs=3,
        dropout=0.2,             # 分类头 dropout，减少过拟合
        verbose=True,
        plots=True,              # 保存训练曲线图
    )

    return results


# ============================================================
# 评估（test 集）
# ============================================================

def evaluate(run_dir: Path):
    from ultralytics import YOLO

    best_pt = run_dir / "weights" / "best.pt"
    if not best_pt.exists():
        print("[eval] 未找到 best.pt，跳过评估")
        return {}

    print(f"\n[eval] 在 test 集上评估: {best_pt}")
    model = YOLO(str(best_pt))
    metrics = model.val(
        data=str(DATASET_DIR),
        split="test",
        imgsz=224,
        verbose=True,
    )

    # 提取关键指标
    top1 = float(metrics.top1) if hasattr(metrics, "top1") else None
    top5 = float(metrics.top5) if hasattr(metrics, "top5") else None
    result = {"top1_accuracy": top1, "top5_accuracy": top5}
    print(f"[eval] Top-1 Accuracy: {top1:.4f}" if top1 else "[eval] Top-1: N/A")
    print(f"[eval] Top-5 Accuracy: {top5:.4f}" if top5 else "[eval] Top-5: N/A")
    return result


# ============================================================
# 保存最优模型到 backend/models/
# ============================================================

def export_best(run_dir: Path, eval_metrics: dict, model_name: str, elapsed: float):
    best_pt  = run_dir / "weights" / "best.pt"
    dest_pt  = MODELS_DIR / "plant_disease_best.pt"

    if not best_pt.exists():
        print("[export] 未找到 best.pt，跳过导出")
        return

    shutil.copy2(best_pt, dest_pt)
    print(f"\n[export] 已复制最优模型 -> {dest_pt}")

    report = {
        "model_name": model_name,
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "dataset": str(DATASET_DIR),
        "weights": str(dest_pt),
        "metrics": eval_metrics,
    }
    report_path = MODELS_DIR / "train_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[export] 训练报告 -> {report_path}")


# ============================================================
# 主入口
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(description="PlantVillage YOLO11 分类训练")
    parser.add_argument("--model",   default="yolo11n-cls",
                        choices=["yolo11n-cls", "yolo11s-cls", "yolo11m-cls"],
                        help="模型规模 (n=最快, s=均衡, m=最准)")
    parser.add_argument("--epochs",  type=int, default=50)
    parser.add_argument("--batch",   type=int, default=32,
                        help="显存不足时改为 16")
    parser.add_argument("--patience",type=int, default=10,
                        help="早停轮数，0 表示禁用")
    return parser.parse_args()


def main():
    args = parse_args()

    if not DATASET_DIR.exists():
        print("[error] 数据集目录不存在，请先运行 scripts/prepare_dataset.py")
        return

    print("=" * 60)
    print("PlantVillage 病虫害分类 - 模型训练")
    print("=" * 60)

    t0 = time.time()
    train(args.model, args.epochs, args.batch, args.patience)
    elapsed = time.time() - t0

    run_dir = RUNS_DIR / "plant_disease"
    eval_metrics = evaluate(run_dir)
    export_best(run_dir, eval_metrics, args.model, elapsed)

    print("\n" + "=" * 60)
    print(f"训练完成！耗时 {elapsed/60:.1f} 分钟")
    print(f"最优模型: {MODELS_DIR / 'plant_disease_best.pt'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
