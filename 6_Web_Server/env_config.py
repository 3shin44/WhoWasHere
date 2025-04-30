import os

from dotenv import load_dotenv

load_dotenv()  # 讀取 .env 檔案


class Config:
    WS_DATABASE_FOLDER = os.getenv("WS_DATABASE_FOLDER")
    WS_DATABASE_NAME = os.getenv("WS_DATABASE_NAME")
    WS_NGINX_HOST = os.getenv("WS_NGINX_HOST")
