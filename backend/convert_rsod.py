import os
import xml.etree.ElementTree as ET
import shutil
import random

# RSOD 数据集类别映射
CLASSES = ["aircraft", "oiltank", "overpass", "playground"]
CLASS_MAP = {cls: idx for idx, cls in enumerate(CLASSES)}


def convert_xml_to_yolo(xml_path):
    """
    将单个 XML 文件转换为 YOLO 格式，并自动从 XML 中读取图片真实宽高
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # 动态获取图片真实的宽高
    size = root.find("size")
    if size is None:
        print(f"警告：{xml_path} 缺失 <size> 标签，无法转换。")
        return None

    image_width = float(size.find("width").text)
    image_height = float(size.find("height").text)

    # 如果宽或高为 0，避免除以 0 报错
    if image_width == 0 or image_height == 0:
        return None

    lines = []
    for obj in root.findall("object"):
        name = obj.find("name").text
        if name not in CLASS_MAP:
            continue

        class_id = CLASS_MAP[name]
        bbox = obj.find("bndbox")
        xmin = float(bbox.find("xmin").text)
        ymin = float(bbox.find("ymin").text)
        xmax = float(bbox.find("xmax").text)
        ymax = float(bbox.find("ymax").text)

        # 转换为 YOLO 格式（归一化）
        x_center = (xmin + xmax) / 2.0 / image_width
        y_center = (ymin + ymax) / 2.0 / image_height
        bbox_width = (xmax - xmin) / image_width
        bbox_height = (ymax - ymin) / image_height

        lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}")

    return "\n".join(lines)


def convert_dataset(base_dir, split_ratio=0.8, seed=42):
    # 路径配置
    archive_dir = os.path.join(base_dir, "data", "rsod", "archive")
    output_dir = os.path.join(base_dir, "data", "rsod", "yolo_dataset")

    train_images_dir = os.path.join(output_dir, "images", "train")
    val_images_dir = os.path.join(output_dir, "images", "val")
    train_labels_dir = os.path.join(output_dir, "labels", "train")
    val_labels_dir = os.path.join(output_dir, "labels", "val")

    # 创建输出目录
    for d in [train_images_dir, val_images_dir, train_labels_dir, val_labels_dir]:
        os.makedirs(d, exist_ok=True)

    dataset_pairs = []

    # 遍历 archive 下的各个类别文件夹获取所有数据对
    for category in CLASSES:
        cat_dir = os.path.join(archive_dir, category)
        images_dir = os.path.join(cat_dir, "JPEGImages")

        # 【重点修改】这里适配了你截图中 Annotation 下面还有一层 xml 文件夹的情况
        annotations_dir = os.path.join(cat_dir, "Annotation", "xml")

        # 增加鲁棒性：如果不存在 xml 子文件夹，就退回到直接在 Annotation 下面找
        if not os.path.exists(annotations_dir):
            annotations_dir = os.path.join(cat_dir, "Annotation")

        if not os.path.exists(images_dir) or not os.path.exists(annotations_dir):
            print(f"提示: 未找到 {category} 的数据文件夹，已跳过。路径: {annotations_dir}")
            continue

        # 获取当前类别下的所有图片
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                basename = os.path.splitext(filename)[0]
                xml_path = os.path.join(annotations_dir, f"{basename}.xml")
                img_path = os.path.join(images_dir, filename)

                # 只有当图片和 XML 都存在时，才加入待处理列表
                if os.path.exists(xml_path):
                    dataset_pairs.append((img_path, xml_path, filename, basename))

    if not dataset_pairs:
        print("未找到任何有效的数据，请检查目录结构！")
        return

    # 随机打乱并分割
    random.seed(seed)
    random.shuffle(dataset_pairs)

    split_idx = int(len(dataset_pairs) * split_ratio)
    train_pairs = dataset_pairs[:split_idx]
    val_pairs = dataset_pairs[split_idx:]

    print(f"找到数据：训练集 {len(train_pairs)} 张，验证集 {len(val_pairs)} 张。正在处理中...")

    # 处理数据的核心逻辑提取为一个内部函数
    def process_data(pairs, target_img_dir, target_lbl_dir):
        for img_path, xml_path, filename, basename in pairs:
            # 1. 转换标注内容并获取真实大小
            label_content = convert_xml_to_yolo(xml_path)

            if label_content is not None:
                # 2. 只有标注转换成功了，才复制图片和写入 txt
                dst_image = os.path.join(target_img_dir, filename)
                shutil.copy(img_path, dst_image)

                with open(os.path.join(target_lbl_dir, f"{basename}.txt"), "w") as f:
                    f.write(label_content)

    # 执行处理
    process_data(train_pairs, train_images_dir, train_labels_dir)
    process_data(val_pairs, val_images_dir, val_labels_dir)

    print(f"数据集转换完成！输出目录：{output_dir}")

    # 创建数据集配置文件
    create_yaml_config(output_dir)


def create_yaml_config(output_dir):
    """创建 YOLO 数据集配置文件"""
    yaml_content = f"""# RSOD 数据集配置文件
path: {os.path.abspath(output_dir)}

train: images/train
val: images/val

nc: {len(CLASSES)}
names: {CLASSES}
"""
    yaml_path = os.path.join(output_dir, "rsod.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print(f"配置文件已创建：{yaml_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    convert_dataset(base_dir)