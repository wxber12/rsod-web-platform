import logging
import sys
from pathlib import Path

class ColoredFormatter(logging.Formatter):
    """
    彩色日志格式化器
    为什么需要自定义 Formatter？
    - 默认的 Formatter 输出没有颜色
    - 不同级别的日志用不同颜色，方便快速识别
    - 只在终端显示颜色，重定向到文件时自动去除
    """
    # ANSI 转义序列 - 用于在终端中显示颜色
    COLORS = {
        'DEBUG': '\033[36m',     # 青色 - 表示详细信息
        'INFO': '\033[32m',      # 绿色 - 表示正常运行
        'WARNING': '\033[33m',   # 黄色 - 表示需要注意
        'ERROR': '\033[31m',     # 红色 - 表示错误
        'CRITICAL': '\033[35m',  # 紫色 - 表示严重错误
        'RESET': '\033[0m'       # 重置颜色
    }

    def format(self, record):
        """
        格式化日志记录
        为什么要覆盖 format 方法？
        - 默认只返回消息内容
        - 我们要动态添加颜色
        """
        levelname = record.levelname
        if levelname in self.COLORS:
            # 为级别名称添加颜色
            # 例如："ERROR" 变成 "\033[31mERROR\033[0m"
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        # 调用父类的 format 方法完成实际格式化
        return super().format(record)

def setup_logging(
    level="INFO",
    log_file=None,
    log_dir=None,
    use_colors=True,
    name=None):
    """
    统一日志配置函数
    参数说明：
        level: 日志级别
              - "DEBUG": 最详细，包含所有调试信息
              - "INFO": 正常运行信息
              - "WARNING": 警告信息
              - "ERROR": 错误信息
              - "CRITICAL": 严重错误
        log_file: 日志文件名
                 - 如果指定，日志会同时保存到文件
                 - 文件保存在 log_dir 目录下
        log_dir: 日志目录
                - 如果指定，使用此目录
                - 如果不指定，使用 data/logs/
        use_colors: 是否使用彩色输出
                   - 默认 True
                   - 如果输出重定向到文件，自动禁用
        name: logger 名称
             - 如果指定，使用命名 logger
             - 如果不指定，使用根 logger
    为什么这些参数有默认值？
    - 大多数情况用默认配置就行
    - 需要特殊配置时再覆盖
    """
    # 统一日志格式：时间 - 模块名 - 级别 - 消息
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 根据是否使用颜色选择格式化器
    # sys.stdout.isatty() 检查是否输出到终端
    # 如果重定向到文件，颜色代码会被写入文件，所以我们禁用它
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        formatter = logging.Formatter(log_format, datefmt=date_format)

    # 获取 logger 实例
    logger = logging.getLogger(name)

    # 设置日志级别
    # getattr(logging, level.upper(), ...) 安全地获取属性
    # 如果 level 不是有效值，默认使用 INFO
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 清除已有的 handlers
    # 为什么？避免重复配置时产生多个 handler
    # 每次调用 setup_logging 都会重新配置
    logger.handlers.clear()

    # 添加控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 如果指定了日志文件，添加文件输出
    if log_file:
        # 确定日志目录
        if log_dir:
            log_path = Path(log_dir)
        else:
            # 默认使用项目 data/logs 目录
            try:
                from app.utils.paths import Paths
                log_path = Paths.data() / "logs"
            except ImportError:
                # 备用方案，如果 Paths 不可用
                log_path = Path("data/logs")

        # 确保目录存在
        log_path.mkdir(parents=True, exist_ok=True)
        log_file_path = log_path / log_file

        # 添加文件 handler
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
        logger.addHandler(file_handler)

    return logger

# 预定义的日志配置 - 针对不同场景优化
def setup_production_logging():
    """
    生产环境日志配置
    特点：
    - INFO 级别：记录正常流程，不过多输出
    - 保存到文件：方便事后分析
    - 不使用颜色：日志文件不需要颜色
    """
    return setup_logging(level="INFO", log_file="app.log")

def setup_debug_logging():
    """
    调试环境日志配置
    特点：
    - DEBUG 级别：记录所有信息
    - 保存详细日志到文件
    - 方便排查问题
    """
    return setup_logging(level="DEBUG", log_file="debug.log")

def setup_training_logging():
    """
    训练脚本日志配置
    特点：
    - INFO 级别：记录训练进度
    - 保存到独立文件
    - 方便追踪训练过程
    """
    return setup_logging(level="INFO", log_file="training.log")
