"""
RSOD 数据集预处理脚本
功能：解压4个zip → 解析自定义txt标注 → 转换为YOLO格式 → 划分train/val/test → 生成rsod.yaml
用法：python scripts/rsod/prepare_dataset.py
"""

import os
import random
import shutil
import zipfile
import json
from pathlib import Path
from PIL import Image

# ============================================================
# 路径配置
# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DIR      = PROJECT_ROOT / "backend" / "data" / "rsod"
OUTPUT_DIR   = RAW_DIR / "yolo_dataset"
MODELS_DIR   = PROJECT_ROOT / "backend" / "models" / "rsod"

CLASSES    = ["aircraft", "oiltank", "overpass", "playground"]
CLASS_MAP  = {cls: idx for idx, cls in enumerate(CLASSES)}

TRAIN_RATIO = 0.8
VAL_RATIO   = 0.1
# test = 剩余 0.1

SEED = 42


# ============================================================
# 解压
# ============================================================

def extract_zips():
    extract_dir = RAW_DIR / "_extracted"
    for cls in CLASSES:
        zip_path = RAW_DIR / f"{cls}.zip"
        if not zip_path.exists():
            print(f"[warn] 未找到 {zip_path}，跳过")
            continue
        dst = extract_dir / cls
        if dst.exists():
            print(f"[extract] 已存在，跳过: {dst}")
            continue
        print(f"[extract] 解压 {zip_path.name} ...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)
        print(f"[extract] 完成 -> {dst}")
    return extract_dir


# ============================================================
# 解析标注（自定义txt格式）
# ============================================================
# 格式：{filename}\t{class_name}\t{xmin}\t{ymin}\t{xmax}\t{ymax}
# 每行一个目标，同一图片可能有多行

def parse_label_file(label_path: Path) -> list[dict]:
    boxes = []
    for line in label_path.read_text(encoding="utf-8", errors="ignore").strip().splitlines():
        parts = line.strip().split()
        if len(parts) < 6:
            continue
        # filename class xmin ymin xmax ymax
        cls_name = parts[1]
        if cls_name not in CLASS_MAP:
            continue
        try:
            xmin, ymin, xmax, ymax = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
        except ValueError:
            continue
        boxes.append({"class_id": CLASS_MAP[cls_name], "xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax})
    return boxes


def to_yolo_line(box: dict, img_w: int, img_h: int) -> str:
    x_center = (box["xmin"] + box["xmax"]) / 2.0 / img_w
    y_center = (box["ymin"] + box["ymax"]) / 2.0 / img_h
    width    = (box["xmax"] - box["xmin"]) / img_w
    height   = (box["ymax"] - box["ymin"]) / img_h
    # 防止超出 [0,1]
    x_center = max(0.0, min(1.0, x_center))
    y_center = max(0.0, min(1.0, y_center))
    width    = max(0.0, min(1.0, width))
    height   = max(0.0, min(1.0, height))
    return f"{box['class_id']} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"


# ============================================================
# 收集所有样本
# ============================================================

def collect_samples(extract_dir: Path) -> list[dict]:
    samples = []
    for cls in CLASSES:
        cls_dir    = extract_dir / cls
        img_dir    = cls_dir / "JPEGImages"
        label_dir  = cls_dir / "Annotation" / "labels"
        if not img_dir.exists():
            print(f"[warn] 图片目录不存在: {img_dir}")
            continue
        for img_path in sorted(img_dir.glob("*.jpg")):
            label_path = label_dir / (img_path.stem + ".txt")
            if not label_path.exists():
                continue
            boxes = parse_label_file(label_path)
            if not boxes:
                continue
            samples.append({"img_path": img_path, "label_path": label_path, "boxes": boxes, "cls": cls})
    print(f"[collect] 共收集 {len(samples)} 张有效图片")
    return samples


# ============================================================
# 划分并写出 YOLO 数据集
# ============================================================

def split_and_write(samples: list[dict]):
    random.seed(SEED)
    random.shuffle(samples)

    n = len(samples)
    n_train = int(n * TRAIN_RATIO)
    n_val   = int(n * VAL_RATIO)

    splits = {
        "train": samples[:n_train],
        "val":   samples[n_train: n_train + n_val],
        "test":  samples[n_train + n_val:],
    }

    for split, subset in splits.items():
        print(f"[split] {split}: {len(subset)} 张")
        img_out   = OUTPUT_DIR / "images" / split
        label_out = OUTPUT_DIR / "labels" / split
        img_out.mkdir(parents=True, exist_ok=True)
        label_out.mkdir(parents=True, exist_ok=True)

        for item in subset:
            # 复制图片
            dst_img = img_out / item["img_path"].name
            shutil.copy2(item["img_path"], dst_img)

            # 读取图片尺寸
            with Image.open(dst_img) as im:
                img_w, img_h = im.size

            # 写出 YOLO 标注
            yolo_lines = [to_yolo_line(b, img_w, img_h) for b in item["boxes"]]
            (label_out / (item["img_path"].stem + ".txt")).write_text(
                "\n".join(yolo_lines), encoding="utf-8"
            )

    return {k: len(v) for k, v in splits.items()}


# ============================================================
# 生成 rsod.yaml
# ============================================================

def create_yaml(split_counts: dict):
    yaml_path = OUTPUT_DIR / "rsod.yaml"
    yaml_content = f"""# RSOD 遥感目标检测数据集配置
path: {OUTPUT_DIR}

train: images/train
val:   images/val
test:  images/test

nc: {len(CLASSES)}
names: {CLASSES}

# 数据集统计
# train: {split_counts['train']} images
# val:   {split_counts['val']} images
# test:  {split_counts['test']} images
"""
    yaml_path.write_text(yaml_content, encoding="utf-8")
    print(f"[yaml] 配置文件 -> {yaml_path}")
    return yaml_path


# ============================================================
# 保存数据集统计
# ============================================================

def save_stats(samples: list[dict], split_counts: dict):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    per_class = {cls: 0 for cls in CLASSES}
    for s in samples:
        per_class[s["cls"]] += 1
    stats = {
        "total_images": len(samples),
        "per_class_images": per_class,
        "split": split_counts,
        "classes": CLASSES,
        "yolo_dataset": str(OUTPUT_DIR),
    }
    stats_path = RAW_DIR / "dataset_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[stats] 统计信息 -> {stats_path}")


# ============================================================
# 主入口
# ============================================================

def main():
    print("=" * 60)
    print("RSOD 数据集预处理")
    print("=" * 60)

    if not RAW_DIR.exists():
        print(f"[error] 数据目录不存在: {RAW_DIR}")
        return

    # 检查zip文件
    missing = [cls for cls in CLASSES if not (RAW_DIR / f"{cls}.zip").exists()]
    if missing:
        print(f"[error] 缺少以下zip文件: {missing}")
        return

    if OUTPUT_DIR.exists():
        print(f"[info] 输出目录已存在，将覆盖: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)

    extract_dir  = extract_zips()
    samples      = collect_samples(extract_dir)
    split_counts = split_and_write(samples)
    yaml_path    = create_yaml(split_counts)
    save_stats(samples, split_counts)

    print("\n" + "=" * 60)
    print(f"预处理完成！共 {len(samples)} 张图片")
    print(f"  train: {split_counts['train']}  val: {split_counts['val']}  test: {split_counts['test']}")
    print(f"  YOLO数据集: {OUTPUT_DIR}")
    print(f"  配置文件:   {yaml_path}")
    print("=" * 60)
    print(f"\n下一步运行训练：")
    print(f"  python scripts/rsod/train.py")


if __name__ == "__main__":
    main()
