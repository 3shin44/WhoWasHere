import logging
import os
from datetime import datetime

from config_loader import load_config


def setup_logger(config_path="configs/default_config.yaml"):
    """設置日誌記錄器"""
    config = load_config(config_path)
    app_name = config["app"]["name"]
    log_dir = config["paths"]["log_dir"]

    # 確保日誌目錄存在
    os.makedirs(log_dir, exist_ok=True)

    # 生成日期格式的日誌檔案名稱
    date_str = datetime.now().strftime("%Y%m%d")
    log_filename = f"{app_name}_{date_str}.log"
    log_path = os.path.join(log_dir, log_filename)

    # 配置日誌
    logger = logging.getLogger(app_name)
    log_level = getattr(logging, config["app"]["log_level"].upper(), logging.INFO)
    logger.setLevel(log_level)

    # 避免重複添加處理器
    if not logger.handlers:
        # 文件處理器
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(log_level)

        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 日誌格式
        formatter = logging.Formatter(
            "%(asctime)s - %(filename)s:%(funcName)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加處理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    logger = setup_logger()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
