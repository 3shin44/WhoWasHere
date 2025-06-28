import os

from config_loader import (
    load_config,
)
from dotenv import load_dotenv
from logger import setup_logger
from video_server import VideoServer

# 載入 .env 檔案
load_dotenv()


def main():
    config = load_config()
    logger = setup_logger()
    logger.info(f"Starting {config['app']['name']} v{config['app']['version']}")

    # 從 .env 檔案中讀取配置
    source_url = os.getenv("CS_VIDEO_SOURCE")
    port = int(os.getenv("CS_SERVER_PORT"))
    server = VideoServer(ws_url=source_url, host="0.0.0.0", port=port)
    logger.info(f"source_url {source_url} on port {port}")
    logger.info(f"Starting VideoServer application from {source_url} on port {port}")
    server.run()


if __name__ == "__main__":
    main()
