import time

import cv2
import numpy as np
from config_loader import (
    load_config,
)
from flask import Flask, Response
from logger import setup_logger

# 初始化配置與日誌
config = load_config()
logger = setup_logger()


class VideoServer:
    def __init__(self, source_url, host="0.0.0.0", port=8080):
        """
        初始化 VideoServer 物件

        :param source_url: 視訊來源 URL 或檔案路徑
        :param host: Flask 伺服器的主機位址
        :param port: Flask 伺服器的埠號
        """
        self.source_url = source_url
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        logger.info(
            f"Initializing VideoServer with source: {source_url}, host: {host}, port: {port}"
        )
        self._setup_routes()

    def _setup_routes(self):
        """設定 Flask 路由"""
        logger.info("Setting up Flask routes")
        self.app.add_url_rule("/video", "video_feed", self.video_feed)

    def video_stream_generator(self):
        """生成視訊流"""
        cap = None
        while True:
            if cap is None or not cap.isOpened():
                logger.info(f"Opening video source: {self.source_url}")
                cap = cv2.VideoCapture(self.source_url)

            ret, frame = cap.read()
            if not ret or frame is None:
                logger.warning("Failed to read frame, sending black frame")
                frame = np.zeros((480, 640, 3), dtype=np.uint8)  # 假畫面
                time.sleep(1)
            yield frame

    def generate_frames(self):
        """生成影像幀"""
        for frame in self.video_stream_generator():
            try:
                # 嘗試將影像編碼為 JPEG 格式
                _, buffer = cv2.imencode(".jpg", frame)
                logger.debug("Successfully encoded frame to JPEG")
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
                )
            except Exception as e:
                # 當發生異常時，記錄日誌並拋出異常
                logger.error(f"Error generating frame: {e}")
                raise RuntimeError(f"Error generating frame: {e}")

    def video_feed(self):
        """視訊流路由"""
        logger.info("Video feed requested")
        return Response(
            self.generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    def run(self):
        """啟動 Flask 伺服器"""
        logger.info(f"Starting Flask server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port)


# 主程式
if __name__ == "__main__":
    source_url = "http://127.0.0.1:5500/sample.mp4"
    logger.info("Starting VideoServer application")
    server = VideoServer(source_url=source_url, host="0.0.0.0", port=8080)
    server.run()
