"""
YOLO11 RSOD 遥感目标检测训练脚本
用法：python scripts/rsod/train.py [--model yolo11n] [--epochs 100] [--batch 16]
"""

import argparse
import json
import shutil
import time
from pathlib import Path

# ============================================================
# 路径配置
# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR     = PROJECT_ROOT / "backend" / "data" / "rsod"
YAML_PATH    = DATA_DIR / "yolo_dataset" / "rsod.yaml"
MODELS_DIR   = PROJECT_ROOT / "backend" / "models" / "rsod"
RUNS_DIR     = PROJECT_ROOT / "backend" / "runs" / "rsod"

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
    print(f"[train] 数据集: {YAML_PATH}")

    model = YOLO(f"{model_name}.pt")

    model.train(
        data=str(YAML_PATH),
        epochs=epochs,
        imgsz=640,
        batch=batch,
        patience=patience,
        device=device,
        project=str(RUNS_DIR),
        name="rsod",
        exist_ok=True,
        optimizer="AdamW",
        lr0=0.01,
        lrf=0.01,
        weight_decay=0.0005,
        warmup_epochs=3,
        verbose=True,
        plots=True,
    )


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
        data=str(YAML_PATH),
        split="test",
        imgsz=640,
        verbose=True,
    )

    map50    = float(metrics.box.map50)   if hasattr(metrics, "box") else None
    map5095  = float(metrics.box.map)     if hasattr(metrics, "box") else None
    precision= float(metrics.box.mp)      if hasattr(metrics, "box") else None
    recall   = float(metrics.box.mr)      if hasattr(metrics, "box") else None

    result = {"mAP50": map50, "mAP50-95": map5095, "precision": precision, "recall": recall}
    if map50:
        print(f"[eval] mAP@0.5: {map50:.4f}  mAP@0.5:0.95: {map5095:.4f}")
        print(f"[eval] Precision: {precision:.4f}  Recall: {recall:.4f}")
    return result


# ============================================================
# 保存最优模型
# ============================================================

def export_best(run_dir: Path, eval_metrics: dict, model_name: str, elapsed: float):
    best_pt = run_dir / "weights" / "best.pt"
    dest_pt = MODELS_DIR / "best.pt"

    if not best_pt.exists():
        print("[export] 未找到 best.pt，跳过导出")
        return

    shutil.copy2(best_pt, dest_pt)
    print(f"\n[export] 已复制最优模型 -> {dest_pt}")

    report = {
        "model_name": model_name,
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "dataset": str(YAML_PATH),
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
    parser = argparse.ArgumentParser(description="RSOD YOLO11 目标检测训练")
    parser.add_argument("--model",    default="yolo11n",
                        choices=["yolo11n", "yolo11s", "yolo11m"],
                        help="模型规模 (n=最快, s=均衡, m=最准)")
    parser.add_argument("--epochs",   type=int, default=100)
    parser.add_argument("--batch",    type=int, default=16,
                        help="显存不足时改为 8")
    parser.add_argument("--patience", type=int, default=20,
                        help="早停轮数，0 表示禁用")
    return parser.parse_args()


def main():
    args = parse_args()

    if not YAML_PATH.exists():
        print("[error] rsod.yaml 不存在，请先运行 scripts/rsod/prepare_dataset.py")
        return

    print("=" * 60)
    print("RSOD 遥感目标检测 - 模型训练")
    print("=" * 60)

    t0 = time.time()
    train(args.model, args.epochs, args.batch, args.patience)
    elapsed = time.time() - t0

    run_dir     = RUNS_DIR / "rsod"
    eval_metrics = evaluate(run_dir)
    export_best(run_dir, eval_metrics, args.model, elapsed)

    print("\n" + "=" * 60)
    print(f"训练完成！耗时 {elapsed/60:.1f} 分钟")
    print(f"最优模型: {MODELS_DIR / 'best.pt'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
