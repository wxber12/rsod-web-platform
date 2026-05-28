#!/usr/bin/env python3
"""
RSOD 数据集转换工具 - 完整示例
展示三个优化模块的综合应用：
1. 路径管理：统一管理所有路径
2. 数据验证：转换前自动检查数据质量
3. 统一日志：完整记录转换过程
"""

import sys
import argparse
import xml.etree.ElementTree as ET
import shutil
import random
from pathlib import Path

# ========================================
# 第一部分：统一日志配置与环境初始化
# ========================================
# 确保可以导入 app 模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.utils.logging_utils import setup_logging
from app.utils.paths import Paths
from app.utils.validation import CheckContext, DataValidator, list_validators, CheckLevel

# 配置日志
logger = setup_logging(
    level="DEBUG",
    log_file="convert.log"
)

# ========================================
# 第二部分：使用路径管理
# ========================================
CLASSES = ["aircraft", "oiltank", "overpass", "playground"]
CLASS_MAP = {cls: idx for idx, cls in enumerate(CLASSES)}

class RSODConverter:
    """RSOD 数据集转换器"""
    def __init__(self, split_ratio=0.8, seed=42):
        self.split_ratio = split_ratio
        self.seed = seed
        
        # ✅ 使用 Paths 统一管理路径
        self.rsod_dir = Paths.rsod_data()
        self.yolo_dir = Paths.yolo_dataset()
        
        # 子目录结构
        self.train_images_dir = self.yolo_dir / "images" / "train"
        self.val_images_dir = self.yolo_dir / "images" / "val"
        self.train_labels_dir = self.yolo_dir / "labels" / "train"
        self.val_labels_dir = self.yolo_dir / "labels" / "val"
        
        # 原始数据（根据项目实际结构定位）
        # 如果数据在 archive 目录下，可以通过 Paths 扩展或直接在此定义
        self.annotations_dir = Paths.rsod_annotations()
        self.images_dir = Paths.rsod_images()
        
        # 统计信息
        self.stats = {
            "total_files": 0,
            "train_files": 0,
            "val_files": 0,
            "skipped_files": 0,
            "converted_files": 0
        }

    # ========================================
    # 第三部分：数据验证
    # ========================================
    def _validate_input_data(self):
        """
        使用数据验证子系统检查输入数据
        为什么这个方法这么重要？
        - 早发现问题是解决问题的最佳时机
        - 清晰的错误报告节省调试时间
        - 避免转换到一半才发现问题
        """
        logger.info("开始验证输入数据...")
        logger.info(f"可用验证器: {list_validators()}")
        
        # 创建验证上下文
        context = CheckContext(
            annotations_dir=self.annotations_dir,
            images_dir=self.images_dir,
            classes=CLASSES
        )
        
        # 执行验证并生成报告
        self.validator = DataValidator(context)
        passed = self.validator.validate_and_report()
        
        # 如果验证失败，给出明确提示
        if not passed:
            logger.error("数据验证未通过，请修复上述问题后重试")
            return False
            
        logger.info("数据验证通过，开始转换")
        return True

    def convert(self):
        """执行完整转换流程"""
        logger.info("=" * 60)
        logger.info("开始 RSOD 数据集转换")
        logger.info("=" * 60)
        
        # 1. 初始化目录
        Paths.init_all_dirs()
        
        # 2. 验证数据
        if not self._validate_input_data():
            error_results = [r for r in self.validator.results if r.level == CheckLevel.ERROR]
            if error_results:
                return False

        # 确保输出目录存在
        for dir_path in [
            self.train_images_dir, self.val_images_dir,
            self.train_labels_dir, self.val_labels_dir
        ]:
            Paths.ensure_dir(dir_path)
            logger.debug(f"准备目录: {dir_path}")

        # 3. 获取并分割文件
        # 这里逻辑根据实际文件查找方式调整
        xml_files = list(self.annotations_dir.glob("*.xml"))
        if not xml_files:
            logger.error(f"在 {self.annotations_dir} 未找到任何 XML 文件")
            return False
            
        random.seed(self.seed)
        random.shuffle(xml_files)
        
        split_idx = int(len(xml_files) * self.split_ratio)
        train_files = xml_files[:split_idx]
        val_files = xml_files[split_idx:]
        
        logger.info(f"数据集分割: 训练集 {len(train_files)} 个，验证集 {len(val_files)} 个")
        
        # 4. 转换并复制文件
        self._process_files(train_files, self.train_images_dir, self.train_labels_dir, "train")
        self._process_files(val_files, self.val_images_dir, self.val_labels_dir, "val")
        
        # 5. 创建 YAML 配置
        self._create_yaml_config()
        
        logger.info("=" * 60)
        logger.info("数据集转换完成！")
        logger.info(f"统计: 成功 {self.stats['converted_files']} 个, 跳过 {self.stats['skipped_files']} 个")
        logger.info("=" * 60)
        return True

    def _process_files(self, xml_list, img_dest, lbl_dest, split_name):
        """处理文件转换和复制"""
        logger.info(f"正在转换 {split_name} 集...")
        for xml_path in xml_list:
            basename = xml_path.stem
            # 查找对应的图片
            img_path = None
            for ext in [".jpg", ".jpeg", ".png"]:
                test_path = self.images_dir / f"{basename}{ext}"
                if test_path.exists():
                    img_path = test_path
                    break
            
            if not img_path:
                logger.warning(f"找不到图片: {basename}，跳过该标注")
                self.stats["skipped_files"] += 1
                continue
            
            # 转换 XML
            yolo_content = self._xml_to_yolo(xml_path)
            if yolo_content:
                # 复制图片
                shutil.copy(img_path, img_dest / img_path.name)
                # 写入标签
                with open(lbl_dest / f"{basename}.txt", "w", encoding="utf-8") as f:
                    f.write(yolo_content)
                self.stats["converted_files"] += 1
            else:
                self.stats["skipped_files"] += 1

    def _xml_to_yolo(self, xml_path):
        """将单个 XML 转换为 YOLO 格式"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            size = root.find("size")
            if size is None: return None
            
            w = float(size.find("width").text)
            h = float(size.find("height").text)
            if w == 0 or h == 0: return None
            
            lines = []
            for obj in root.findall("object"):
                name = obj.find("name").text
                if name not in CLASS_MAP: continue
                
                class_id = CLASS_MAP[name]
                bbox = obj.find("bndbox")
                xmin = float(bbox.find("xmin").text)
                ymin = float(bbox.find("ymin").text)
                xmax = float(bbox.find("xmax").text)
                ymax = float(bbox.find("ymax").text)
                
                # 归一化
                x_center = (xmin + xmax) / 2.0 / w
                y_center = (ymin + ymax) / 2.0 / h
                bw = (xmax - xmin) / w
                bh = (ymax - ymin) / h
                
                lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}")
            
            return "\n".join(lines)
        except Exception as e:
            logger.debug(f"转换文件 {xml_path.name} 失败: {e}")
            return None

    def _create_yaml_config(self):
        """创建数据集配置文件"""
        yaml_content = f"""# RSOD 数据集配置文件
path: {self.yolo_dir.absolute()}
train: images/train
val: images/val
nc: {len(CLASSES)}
names: {CLASSES}
"""
        yaml_path = self.yolo_dir / "rsod.yaml"
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        logger.info(f"配置文件已创建: {yaml_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RSOD 数据集转换工具")
    parser.add_argument("--split", type=float, default=0.8, help="分割比例")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    args = parser.parse_args()
    
    converter = RSODConverter(split_ratio=args.split, seed=args.seed)
    success = converter.convert()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
