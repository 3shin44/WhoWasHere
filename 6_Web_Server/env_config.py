import os
from dotenv import load_dotenv

load_dotenv()  # 讀取 .env 檔案

class Config:
    WS_DATABASE_URI = os.getenv('WS_DATABASE_URI')
    WS_IMG_FOLDER = os.getenv('WS_IMG_FOLDER')