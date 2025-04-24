import hashlib
import os
import random
import time

from config_loader import (
    load_config,
)
from logger import setup_logger
from person_detector import PersonDetector, PersonDetectorYOLO8
from util import frame_to_base64, frame_to_jpg, get_datetime_string


def detection_callback(label, confidence, frame, folder_path="./test/v8"):
    print(f"Detected {label} with confidence {confidence:.2f} at {frame}")
    # 生成雜湊值
    unique_string = f"{get_datetime_string()}_{label}_{random.random()}"
    hash_object = hashlib.md5(unique_string.encode())
    hash_postfix = hash_object.hexdigest()[:5]  # 取前5碼

    # 儲存檔案
    frame_to_jpg(
        frame, folder_path, f"{get_datetime_string()}_{label}_{hash_postfix}.jpg"
    )


def main():
    config = load_config()
    logger = setup_logger()
    logger.info(f"Starting {config['app']['name']} v{config['app']['version']}")

    video_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "./test/sample/japan_sample2.mp4"
    )
    frame_interval = 30

    # detector = PersonDetector(video_source=video_path, threshold=0.5, callback=detection_callback)
    # detector.process_video(frame_interval)

    # detector_v8 = PersonDetectorYOLO8(video_source=video_path, threshold=0.5, callback=detection_callback)
    # detector_v8.process_video(frame_interval)


if __name__ == "__main__":
    main()
