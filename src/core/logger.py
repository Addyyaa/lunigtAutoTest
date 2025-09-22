"""日志模块

职责：
- 提供统一的 Logger，输出到控制台与 `logs/<name>.log`
- 采用滚动文件策略，避免日志过大
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = "tests", level: int = logging.INFO) -> logging.Logger:
    """创建或获取指定名称的 logger。

    - 首次调用时初始化控制台与文件处理器
    - 后续相同名称复用同一实例，避免重复 handler
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)

    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"{name}.log"

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(log_file, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(fmt)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
