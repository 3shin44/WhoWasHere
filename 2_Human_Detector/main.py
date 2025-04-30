import json
import os
from datetime import datetime
from functools import partial

from config_loader import (
    load_config,
)
from dotenv import load_dotenv
from logger import setup_logger
from person_detector import PersonDetector
from redis_client import RedisClient
from util import frame_to_base64


def detection_callback(label, confidence, frame, redis_client, list_name, ttl=60):
    # Callback 收到判斷後往REDIS丟 整理檔案由後續服務來寫 避免此處同時處理檔案
    json_value = {
        "capture_datetime": datetime.now().isoformat(),  # ISO 8601 format
        "img_base64": frame_to_base64(frame),
        "predict_probability": f"{confidence:.2f}",
        "class_label": label,
    }
    redis_client.write_to_list(list_name, json.dumps(json_value), ttl)


def main():
    config = load_config()
    logger = setup_logger()
    logger.info(f"Starting {config['app']['name']} v{config['app']['version']}")

    # 讀取本地設定檔
    load_dotenv()
    list_name = os.getenv("HD_REDIS_QUEUE")
    ttl = int(os.getenv("HD_REDIS_QUEUE_TTL"))
    frame_interval = int(os.getenv("HD_FRAME_INTERVAL"))
    threshold = float(os.getenv("HD_THRESHOLD"))

    # 實體化REDIS
    redis_client = RedisClient()

    # 綁定CALLBACK參數
    callback_with_instance = partial(
        detection_callback, redis_client=redis_client, list_name=list_name, ttl=ttl
    )

    # 設定影片來源
    video_path = os.getenv("HD_VIDEO_SOURCE")

    # 實體化模型, 啟動辨識 (tiny)
    detector_tiny = PersonDetector(
        video_source=video_path, threshold=threshold, callback=callback_with_instance
    )
    detector_tiny.process_video(frame_interval)

    # 實體化模型, 啟動辨識 (v8 硬體需求較高)
    # detector_v8 = PersonDetectorYOLO8(
    #     video_source=video_path, threshold=threshold, callback=callback_with_instance
    # )
    # detector_v8.process_video(frame_interval)


if __name__ == "__main__":
    main()
