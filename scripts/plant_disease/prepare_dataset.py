"""
PlantVillage 数据集预处理脚本
功能：解压 -> 分析 -> 数据增强（平衡类别）-> 划分 train/val/test
输出目录：D:/rsod-web-platform/dataset/
"""

import os
import sys
import zipfile
import shutil
import random
import json
from pathlib import Path
from collections import Counter

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

# ============================================================
# 配置
# ============================================================
ZIP_PATH    = Path("D:/datasets/PlantVillage/raw/Plant_leaf_diseases_dataset_without_augmentation.zip")
OUTPUT_DIR  = Path("D:/rsod-web-platform/dataset")
WORK_DIR    = OUTPUT_DIR / "_extracted"   # 临时解压目录

IMG_SIZE    = 224          # 统一缩放尺寸
TRAIN_RATIO = 0.8
VAL_RATIO   = 0.1
TEST_RATIO  = 0.1

# 每类最少样本数（不足则通过增强补齐）
MIN_SAMPLES_PER_CLASS = 1000
# 每类最多保留的增强样本上限，避免单类过大
MAX_SAMPLES_PER_CLASS = 2000

# 不需要的类（背景图，对病虫害识别无意义）
EXCLUDE_CLASSES = {"Background_without_leaves"}

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ============================================================
# 工具函数
# ============================================================

def log(msg: str):
    print(f"[prepare] {msg}", flush=True)


def resize_img(img: Image.Image) -> Image.Image:
    return img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)


# ---------- 单张图增强变体（返回 PIL Image） ----------

def aug_flip(img: Image.Image) -> Image.Image:
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def aug_rotate(img: Image.Image, angle: int) -> Image.Image:
    return img.rotate(angle, expand=False, fillcolor=(0, 0, 0))


def aug_brightness(img: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Brightness(img).enhance(factor)


def aug_contrast(img: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Contrast(img).enhance(factor)


def aug_saturation(img: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Color(img).enhance(factor)


def aug_blur(img: Image.Image) -> Image.Image:
    return img.filter(ImageFilter.GaussianBlur(radius=1))


def aug_crop_pad(img: Image.Image, crop_ratio: float = 0.9) -> Image.Image:
    """随机裁剪后再缩回原尺寸"""
    w, h = img.size
    new_w, new_h = int(w * crop_ratio), int(h * crop_ratio)
    x = random.randint(0, w - new_w)
    y = random.randint(0, h - new_h)
    return img.crop((x, y, x + new_w, y + new_h)).resize((w, h), Image.LANCZOS)


# 所有增强变体定义（函数, kwargs）
AUG_PIPELINE = [
    (aug_flip,       {}),
    (aug_rotate,     {"angle":  15}),
    (aug_rotate,     {"angle": -15}),
    (aug_rotate,     {"angle":  30}),
    (aug_brightness, {"factor": 1.3}),
    (aug_brightness, {"factor": 0.7}),
    (aug_contrast,   {"factor": 1.3}),
    (aug_contrast,   {"factor": 0.7}),
    (aug_saturation, {"factor": 1.4}),
    (aug_saturation, {"factor": 0.6}),
    (aug_blur,       {}),
    (aug_crop_pad,   {"crop_ratio": 0.88}),
    (aug_crop_pad,   {"crop_ratio": 0.92}),
    # 组合增强
    (lambda img: aug_flip(aug_rotate(img, 10)),  {}),
    (lambda img: aug_brightness(aug_flip(img), 1.2), {}),
]


def generate_augmented(src: Image.Image, n_needed: int) -> list[Image.Image]:
    """从一张图生成最多 n_needed 张增强图（循环使用 pipeline）"""
    results = []
    pipeline = AUG_PIPELINE[:]
    random.shuffle(pipeline)
    idx = 0
    while len(results) < n_needed:
        fn, kwargs = pipeline[idx % len(pipeline)]
        results.append(fn(src, **kwargs))
        idx += 1
    return results[:n_needed]


# ============================================================
# Step 1: 解压
# ============================================================

def extract_zip():
    if WORK_DIR.exists():
        log(f"解压目录已存在，跳过解压：{WORK_DIR}")
        return

    log(f"开始解压 {ZIP_PATH.name} ...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(WORK_DIR)
    log("解压完成")


def find_class_dirs() -> dict[str, Path]:
    """返回 {类名: 类目录路径}"""
    # zip 解压后的根目录通常是 Plant_leave_diseases_dataset_without_augmentation/
    roots = [p for p in WORK_DIR.iterdir() if p.is_dir()]
    assert roots, "解压后未找到子目录"
    base = roots[0]  # e.g. Plant_leave_diseases_dataset_without_augmentation

    class_dirs = {}
    for d in sorted(base.iterdir()):
        if d.is_dir() and d.name not in EXCLUDE_CLASSES:
            class_dirs[d.name] = d
    return class_dirs


# ============================================================
# Step 2: 分析类别分布
# ============================================================

def analyze(class_dirs: dict[str, Path]) -> dict[str, list[Path]]:
    """返回 {类名: [图片路径列表]}"""
    class_images: dict[str, list[Path]] = {}
    for cls, d in class_dirs.items():
        imgs = sorted(p for p in d.iterdir()
                      if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"})
        class_images[cls] = imgs

    counts = {cls: len(imgs) for cls, imgs in class_images.items()}
    log(f"共 {len(counts)} 个类别，总图片数 {sum(counts.values())}")
    log(f"最多: {max(counts, key=counts.get)} ({max(counts.values())}张)")
    log(f"最少: {min(counts, key=counts.get)} ({min(counts.values())}张)")
    log(f"中位数: {sorted(counts.values())[len(counts)//2]} 张")

    return class_images


# ============================================================
# Step 3: 增强 + 划分
# ============================================================

def process_split(
    cls: str,
    img_paths: list[Path],
    split_dirs: dict[str, Path],
):
    """
    对一个类：
    1. 打乱 -> 划分原始图为 train/val/test
    2. 如果 train 不足 MIN_SAMPLES_PER_CLASS，对 train 做增强补齐
    3. 将所有图片缩放到 IMG_SIZE 后写入对应目录
    """
    random.shuffle(img_paths)
    n = len(img_paths)
    n_test  = max(1, int(n * TEST_RATIO))
    n_val   = max(1, int(n * VAL_RATIO))
    n_train = n - n_val - n_test

    splits = {
        "train": img_paths[:n_train],
        "val":   img_paths[n_train:n_train + n_val],
        "test":  img_paths[n_train + n_val:],
    }

    stats = {}

    for split_name, paths in splits.items():
        dst_dir = split_dirs[split_name] / cls
        dst_dir.mkdir(parents=True, exist_ok=True)

        saved = 0
        for src_path in paths:
            try:
                img = Image.open(src_path).convert("RGB")
                img = resize_img(img)
                img.save(dst_dir / src_path.name, quality=95)
                saved += 1
            except Exception as e:
                log(f"  警告：跳过损坏图片 {src_path.name}: {e}")

        # 对 train 集做增强补齐
        if split_name == "train":
            target = min(MIN_SAMPLES_PER_CLASS, MAX_SAMPLES_PER_CLASS)
            n_aug  = max(0, target - saved)
            aug_count = 0

            if n_aug > 0:
                src_pool = [Image.open(p).convert("RGB") for p in paths[:min(50, len(paths))]]
                aug_idx  = 0
                while aug_count < n_aug:
                    src = src_pool[aug_idx % len(src_pool)]
                    aug_idx += 1
                    variants = generate_augmented(src, 1)
                    aug_img = resize_img(variants[0])
                    aug_img.save(dst_dir / f"aug_{aug_count:05d}.jpg", quality=90)
                    aug_count += 1

            stats["train"] = saved + aug_count
        else:
            stats[split_name] = saved

    return stats


def build_dataset(class_images: dict[str, list[Path]]):
    split_dirs = {
        "train": OUTPUT_DIR / "train",
        "val":   OUTPUT_DIR / "val",
        "test":  OUTPUT_DIR / "test",
    }
    for d in split_dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    all_stats = {}
    total = len(class_images)
    for i, (cls, paths) in enumerate(class_images.items(), 1):
        log(f"[{i:02d}/{total}] 处理类别: {cls} ({len(paths)} 张原始图)")
        stats = process_split(cls, paths, split_dirs)
        all_stats[cls] = stats
        log(f"       -> train={stats['train']}  val={stats['val']}  test={stats['test']}")

    return all_stats


# ============================================================
# Step 4: 生成 dataset.yaml（供 YOLO11 使用）
# ============================================================

def write_yaml(class_names: list[str], stats: dict):
    yaml_path = OUTPUT_DIR / "dataset.yaml"
    names_str = "\n".join(f"  {i}: {n}" for i, n in enumerate(class_names))

    total_train = sum(v["train"] for v in stats.values())
    total_val   = sum(v["val"]   for v in stats.values())
    total_test  = sum(v["test"]  for v in stats.values())

    content = f"""# PlantVillage 病虫害识别数据集
# 自动生成，请勿手动修改

path: {OUTPUT_DIR.as_posix()}
train: train
val:   val
test:  test

nc: {len(class_names)}
names:
{names_str}

# 数据统计
# train: {total_train} 张
# val:   {total_val} 张
# test:  {total_test} 张
# 合计:  {total_train + total_val + total_test} 张
"""
    yaml_path.write_text(content, encoding="utf-8")
    log(f"已生成 dataset.yaml -> {yaml_path}")


def write_stats(stats: dict, class_names: list[str]):
    report_path = OUTPUT_DIR / "dataset_stats.json"
    summary = {
        "num_classes": len(class_names),
        "classes": class_names,
        "per_class": stats,
        "totals": {
            "train": sum(v["train"] for v in stats.values()),
            "val":   sum(v["val"]   for v in stats.values()),
            "test":  sum(v["test"]  for v in stats.values()),
        }
    }
    report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"已生成统计报告 -> {report_path}")


# ============================================================
# 主流程
# ============================================================

def main():
    log("=" * 60)
    log("PlantVillage 数据预处理开始")
    log("=" * 60)

    # 检查输出目录是否已完整
    if (OUTPUT_DIR / "train").exists() and (OUTPUT_DIR / "dataset.yaml").exists():
        log("检测到已处理的数据集，跳过。若需重新处理请删除 dataset/ 目录。")
        sys.exit(0)

    # Step 1
    extract_zip()

    # Step 2
    class_dirs   = find_class_dirs()
    class_images = analyze(class_dirs)
    class_names  = sorted(class_images.keys())

    # Step 3
    log("\n开始数据增强 + 划分（这可能需要几分钟）...")
    stats = build_dataset(class_images)

    # Step 4
    write_yaml(class_names, stats)
    write_stats(stats, class_names)

    total = stats
    log("\n" + "=" * 60)
    log("预处理完成！")
    log(f"  数据集目录: {OUTPUT_DIR}")
    log(f"  train: {sum(v['train'] for v in stats.values())} 张")
    log(f"  val:   {sum(v['val']   for v in stats.values())} 张")
    log(f"  test:  {sum(v['test']  for v in stats.values())} 张")
    log("=" * 60)


if __name__ == "__main__":
    main()
