import time
import threading
import queue
import cv2
import numpy as np
import websocket
import ssl
import av

from flask import Flask, Response
from config_loader import load_config
from logger import setup_logger

# 初始化設定與日誌
config = load_config()
logger = setup_logger()


class VideoServer:
    def __init__(self, ws_url, host="0.0.0.0", port=8080):
        self.ws_url = ws_url
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.frame_queue = queue.Queue(maxsize=10)
        self.decoder = av.codec.CodecContext.create('hevc', 'r')
        self.ws_thread = threading.Thread(target=self._start_ws_client)
        self.ws_thread.daemon = True
        self.ws_started = False
        self.ws_lock = threading.Lock()  # 避免多次啟動 WS
        self._setup_routes()

    def _setup_routes(self):
        self.app.add_url_rule("/video", "video_feed", self.video_feed)

    def _start_ws_client(self):
        def on_message(ws, message):
            if isinstance(message, bytes):
                try:
                    packets = self.decoder.parse(message)
                    for packet in packets:
                        frames = self.decoder.decode(packet)
                        for frame in frames:
                            img = frame.to_ndarray(format='bgr24')
                            if not self.frame_queue.full():
                                self.frame_queue.put(img)
                except av.AVError as e:
                    logger.error(f"[Decode error] {e}")

        def on_open(ws):
            logger.info("[WebSocket Opened] Sending init commands")
            ws.send("Basic YWRtaW46YTExMTExMQ==")
            ws.send("vobits=20,pbits=20,aobits=0,hq=1")

        def on_error(ws, error):
            logger.error(f"[WebSocket Error] {error}")

        def on_close(ws, code, msg):
            logger.warning(f"[WebSocket Closed] {code}: {msg}")

        logger.info(f"[WebSocket Connecting] to {self.ws_url}")
        while True:
            try:
                ws = websocket.WebSocketApp(
                    self.ws_url,
                    header=[
                        "Origin: https://192.168.1.161",
                        "User-Agent: PythonClient/1.0",
                    ],
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                )
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            except Exception as e:
                logger.error(f"[WebSocket Exception] {e}")
            time.sleep(5)

    def ensure_ws_running(self):
        with self.ws_lock:
            if not self.ws_started:
                logger.info("Starting WebSocket thread")
                self.ws_thread.start()
                self.ws_started = True

    def video_stream_generator(self):
        self.ensure_ws_running()

        while True:
            try:
                frame = self.frame_queue.get(timeout=1)
            except queue.Empty:
                logger.warning("No frame in queue, sending black frame")
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
            yield frame
            time.sleep(0.05)

    def generate_frames(self):
        for frame in self.video_stream_generator():
            try:
                _, buffer = cv2.imencode(".jpg", frame)
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    + f"Content-Length: {len(buffer)}\r\n\r\n".encode()
                    + buffer.tobytes()
                    + b"\r\n"
                )
            except Exception as e:
                logger.error(f"Frame encoding error: {e}")

    def video_feed(self):
        logger.info("Video feed requested")
        return Response(
            self.generate_frames(),
            mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    def run(self):
        logger.info(f"Starting Flask server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, threaded=True)


# 主程式執行
if __name__ == "__main__":
    ws_url = "wss://192.168.1.161/streaming"
    logger.info("Starting VideoServer (WS mode)")
    server = VideoServer(ws_url, host="0.0.0.0", port=8080)
    server.run()
