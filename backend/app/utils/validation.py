import sys
import logging
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

# 获取 logger 实例
logger = logging.getLogger(__name__)

class CheckLevel(Enum):
    """
    检查结果级别
    为什么分级而不是简单的 True/False？
    - 不同级别的错误需要不同的处理方式
    - ERROR 应该阻断流程，WARNING 可以继续
    - INFO 用于展示额外信息，不影响判断
    - PASS 用于确认正常状态
    """
    PASS = "pass"       # 通过 - 一切正常
    INFO = "info"       # 信息 - 有用的提示
    WARNING = "warning" # 警告 - 值得关注，但不阻断
    ERROR = "error"     # 错误 - 阻断流程，必须修复

@dataclass
class CheckResult:
    """单个检查结果"""
    level: CheckLevel
    message: str
    check_name: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CheckContext:
    """
    检查上下文 - 验证器的输入数据
    为什么用 dataclass？
    - 自动生成 __init__、__repr__ 等方法
    - 类型提示清晰
    - 方便扩展新参数
    """
    annotations_dir: Optional[Path] = None  # 标注目录
    images_dir: Optional[Path] = None       # 图片目录
    classes: Optional[List[str]] = None     # 期望的类别列表

    # 扩展字段
    image_extensions: List[str] = field(
        default_factory=lambda: [".jpg", ".jpeg", ".png"]
    )
    extra: Dict[str, Any] = field(default_factory=dict)

# 验证器注册表
_validators = {}

def register_validator(name):
    """验证器装饰器"""
    def decorator(func):
        _validators[name] = func
        func._validator_name = name
        return func
    return decorator

def list_validators():
    """获取所有已注册的验证器名称"""
    return list(_validators.keys())

def get_validator(name):
    """获取指定名称的验证器"""
    return _validators.get(name)

class DataValidator:
    """
    数据验证子系统
    核心思想：在执行耗时或关键操作（如训练、转换）前，先进行自动化的数据质量检查
    """
    def __init__(self, context: CheckContext):
        self.context = context
        self.results: List[CheckResult] = []

    def run(self, validator_names: Optional[List[str]] = None):
        """运行指定的或全部验证器"""
        self.results = []
        names = validator_names if validator_names is not None else list_validators()

        for name in names:
            validator = get_validator(name)
            if validator:
                try:
                    check_results = validator(self.context)
                    for r in check_results:
                        if not r.check_name:
                            r.check_name = name
                    self.results.extend(check_results)
                except Exception as e:
                    self.results.append(CheckResult(
                        level=CheckLevel.ERROR,
                        message=f"验证器 {name} 执行失败: {str(e)}",
                        check_name=name
                    ))
        return self.results

    def validate_and_report(self):
        """执行验证并打印精美报告"""
        self.run()
        
        print("\n" + "="*60)
        print("数据验证报告")
        print("="*60)

        error_count = 0
        warning_count = 0
        
        for r in self.results:
            icon = "✅" if r.level == CheckLevel.PASS else \
                   "ℹ️" if r.level == CheckLevel.INFO else \
                   "⚠️" if r.level == CheckLevel.WARNING else "❌"
            
            print(f"{icon} [{r.level.value.upper()}] {r.check_name}: {r.message}")
            
            if r.level == CheckLevel.ERROR:
                error_count += 1
            elif r.level == CheckLevel.WARNING:
                warning_count += 1

        print("-" * 60)
        print(f"总计: {len(self.results)} 项检查  错误: {error_count}  警告: {warning_count}")
        print("=" * 60 + "\n")

        return error_count == 0

@register_validator("directories_exist")
def check_directories(ctx: CheckContext):
    """检查必要目录是否存在"""
    results = []
    if ctx.annotations_dir:
        if ctx.annotations_dir.exists():
            results.append(CheckResult(CheckLevel.PASS, f"标注目录存在: {ctx.annotations_dir}"))
        else:
            results.append(CheckResult(CheckLevel.ERROR, f"标注目录不存在: {ctx.annotations_dir}"))
    
    if ctx.images_dir:
        if ctx.images_dir.exists():
            results.append(CheckResult(CheckLevel.PASS, f"图片目录存在: {ctx.images_dir}"))
        else:
            results.append(CheckResult(CheckLevel.ERROR, f"图片目录不存在: {ctx.images_dir}"))
    return results

@register_validator("annotation_files")
def check_annotation_files(ctx: CheckContext):
    """检查标注文件数量"""
    results = []
    if not ctx.annotations_dir or not ctx.annotations_dir.exists():
        return results
    
    xml_files = list(ctx.annotations_dir.glob("*.xml"))
    if len(xml_files) == 0:
        results.append(CheckResult(CheckLevel.ERROR, "未找到任何 XML 标注文件"))
    else:
        results.append(CheckResult(CheckLevel.PASS, f"找到 {len(xml_files)} 个 XML 标注文件", details={"count": len(xml_files)}))
    return results

@register_validator("image_annotation_match")
def check_image_annotation_match(ctx: CheckContext):
    """检查图片和标注文件是否匹配"""
    results = []
    if not ctx.annotations_dir or not ctx.images_dir:
        return results

    xml_stems = {f.stem for f in ctx.annotations_dir.glob("*.xml")}
    image_stems = set()
    for ext in ctx.image_extensions:
        image_stems.update({f.stem for f in ctx.images_dir.glob(f"*{ext}")})

    missing_images = xml_stems - image_stems
    if missing_images:
        results.append(CheckResult(CheckLevel.WARNING, f"{len(missing_images)} 个标注文件缺少对应图片", details={"missing": list(missing_images)[:10]}))

    missing_xmls = image_stems - xml_stems
    if missing_xmls:
        results.append(CheckResult(CheckLevel.WARNING, f"{len(missing_xmls)} 个图片缺少对应标注", details={"missing": list(missing_xmls)[:10]}))

    if not missing_images and not missing_xmls:
        results.append(CheckResult(CheckLevel.PASS, f"图片和标注文件完全匹配，共 {len(xml_stems & image_stems)} 对"))
    
    return results

@register_validator("class_validation")
def check_classes(ctx: CheckContext):
    """检查标注中的类别是否有效"""
    results = []
    if not ctx.annotations_dir or not ctx.classes:
        return results

    import xml.etree.ElementTree as ET
    classes_set = set(ctx.classes)
    found_classes = set()
    unknown_classes = set()

    for xml_file in list(ctx.annotations_dir.glob("*.xml"))[:100]:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for obj in root.findall("object"):
                name = obj.find("name").text
                found_classes.add(name)
                if name not in classes_set:
                    unknown_classes.add(name)
        except Exception:
            continue

    if found_classes:
        results.append(CheckResult(CheckLevel.INFO, f"数据集中发现的类别: {sorted(found_classes)}"))
    if unknown_classes:
        results.append(CheckResult(CheckLevel.WARNING, f"发现未知类别: {sorted(unknown_classes)}"))
    if not unknown_classes:
        results.append(CheckResult(CheckLevel.PASS, "类别验证通过"))
    
    return results
