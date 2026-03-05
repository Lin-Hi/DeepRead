"""
/**
 * [IN]: logging, logging.handlers, config.settings
 * [OUT]: 全局统一配置的滚动日志实例
 * [POS]: 被所有核心模块使用，用于跟踪系统运行状态与异常隔离
 * [PROTOCOL]: 若添加新的 Handler 或修改输出格式 -> 更新测试用例
 */
"""
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from .config import settings

def _setup_logger() -> logging.Logger:
    """初始化全局单例 Logger"""
    logger = logging.getLogger("deepread")
    
    # 避免重复绑定 handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG)  # 基础收集器级别设为 DEBUG，具体由 handler 拦截
    
    # === 1. 控制台 Handler (INFO 级别，易读短格式) ===
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    console_formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # === 2. 滚动文件 Handler (DEBUG 级别，包含详尽的模块名/行号等线索) ===
    log_dir: Path = settings.log_path
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 按天切割日志，保留 30 天
    file_path = log_dir / "deepread.log"
    file_handler = TimedRotatingFileHandler(
        filename=str(file_path),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s - [%(levelname)s] - %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 禁止将日志向上抛递到 root logger（避免系统双重打印）
    logger.propagate = False
    
    return logger

# 暴露出单例
system_logger = _setup_logger()

def get_logger(name: str) -> logging.Logger:
    """获取带层级名前缀的子 logger，继承 system_logger 的 handlers"""
    return system_logger.getChild(name)
