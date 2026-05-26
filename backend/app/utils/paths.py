#!/usr/bin/env python3
"""
路径管理模块
统一管理项目所有路径，支持从任意子模块定位项目根目录
"""

from pathlib import Path
from typing import Optional

def find_project_root(start_path=None, marker_file=".rsod_platform"):
    """
    从当前位置向上查找项目根目录（通过查找 marker file）
    """
    if start_path is None:
        import inspect
        frame = inspect.stack()[1]
        start_path = Path(frame.filename).parent

    current = Path(start_path).resolve()

    for parent in [current] + list(current.parents):
        marker_path = parent / marker_file
        if marker_path.exists():
            return parent

    raise FileNotFoundError(
        f"Could not find {marker_file} in {current} or any parent directory"
    )

class Paths:
    """
    项目路径管理类
    所有路径统一在此定义，避免硬编码
    """
    _root = None

    @classmethod
    def root(cls):
        """获取项目根目录"""
        if cls._root is None:
            cls._root = find_project_root()
        return cls._root

    @classmethod
    def backend(cls):
        """backend 目录"""
        return cls.root() / "backend"

    @classmethod
    def app(cls):
        """app 目录"""
        return cls.backend() / "app"

    @classmethod
    def data(cls):
        """数据目录"""
        return cls.backend() / "data"

    @classmethod
    def rsod_data(cls):
        """RSOD 数据集目录"""
        return cls.data() / "rsod"

    @classmethod
    def rsod_images(cls):
        """RSOD 原始图片目录"""
        return cls.rsod_data() / "images"

    @classmethod
    def rsod_annotations(cls):
        """RSOD 标注文件目录"""
        return cls.rsod_data() / "annotations"

    @classmethod
    def yolo_dataset(cls):
        """YOLO 格式数据集输出目录"""
        return cls.rsod_data() / "yolo_dataset"

    @classmethod
    def models(cls):
        """模型文件目录"""
        return cls.backend() / "app" / "models"

    @classmethod
    def logs(cls):
        """日志目录"""
        return cls.data() / "logs"

    @classmethod
    def ensure_dir(cls, path: Path):
        """确保目录存在"""
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def init_all_dirs(cls):
        """初始化所有必要的目录结构"""
        dirs = [
            cls.data(),
            cls.rsod_data(),
            cls.rsod_images(),
            cls.rsod_annotations(),
            cls.yolo_dataset(),
            cls.models(),
            cls.logs(),
        ]
        for dir_path in dirs:
            cls.ensure_dir(dir_path)

# 便捷导出
root = Paths.root()
backend_dir = Paths.backend()
app_dir = Paths.app()
data_dir = Paths.data()
