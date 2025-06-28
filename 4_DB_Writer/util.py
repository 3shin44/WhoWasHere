import base64
import json
import os
import uuid
from datetime import datetime
from PIL import Image
import io

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from config_loader import (
    load_config,
)
from logger import setup_logger

config = load_config()
logger = setup_logger()


def convert_json(item):
    """
    將 REDIS傳入資料轉為JSON格式
    """
    try:
        keyname, value = item  # 解構 tuple，取得 keyname 和 JSON 字串
        data = json.loads(value)  # 將 JSON 字串轉換為字典
        return data
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error converting item: {e}")
        raise RuntimeError(f"Error converting item: {e}")


def convert_db_item(item, filename):
    """
    將資料轉換為 SQLite 插入語法所需的參數
    :param item: Tuple 格式資料，例如 ('visitor_queue', '{"capture_datetime": "...", "img_base64": "...", "img_path": "...", "predict_probability": "..."}')
    :return: SQL 插入語法字串和對應的參數
    """
    data = convert_json(item)  # 將 JSON 字串轉換為字典
    insert_query = """
    INSERT INTO capture_log (capture_datetime, img_base64, img_path, predict_probability, class_label) 
    VALUES (?, ?, ?, ?, ?);
    """
    params = (
        data.get("capture_datetime"),
        "", # 暫不儲存 節省空間 data.get("img_base64")
        filename,
        data.get("predict_probability"),
        data.get("class_label"),  # 預設為 None，如果沒有提供 note
    )
    return insert_query, params


def save_to_file(item, max_width=1024, max_height=1024):
    """
    取出 BASE64 轉為 JPG 圖檔，若尺寸過大會自動縮小，然後儲存至指定路徑。
    """
    data = convert_json(item)  # 將 JSON 字串轉換為字典

    # Step 1: 解碼 base64 並轉為 PIL 圖片
    img_base64 = data.get("img_base64")
    if not img_base64:
        raise ValueError("img_base64 is missing")

    try:
        img_data = base64.b64decode(img_base64)
        image = Image.open(io.BytesIO(img_data))

        # 自動調整圖片尺寸（維持比例）
        if image.width > max_width or image.height > max_height:
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # 轉回 bytes 格式以便寫入檔案
        img_bytes_io = io.BytesIO()
        image.save(img_bytes_io, format="JPEG")
        img_data = img_bytes_io.getvalue()
    except Exception as e:
        logger.error(f"Failed to decode or resize image: {e}")
        raise ValueError(f"Invalid image data or base64 input: {e}")

    # Step 2: 解析時間戳
    capture_datetime = data.get("capture_datetime")
    if not capture_datetime:
        logger.error("capture_datetime is missing in the input data.")
        raise ValueError("capture_datetime is missing in the input data.")
    try:
        capture_time = datetime.fromisoformat(capture_datetime)
    except ValueError:
        logger.error("Invalid capture_datetime format. Expected ISO 8601 format.")
        raise ValueError("Invalid capture_datetime format. Expected ISO 8601 format.")

    # Step 3: 檔案命名與儲存路徑
    timestamp = capture_time.strftime("%Y%m%d_%H%M%S_%f")[:-3]
    short_uuid = str(uuid.uuid4())[:5]
    class_label = data.get("class_label", "unknown")
    filename = f"{timestamp}_{class_label}_{short_uuid}.jpg"

    base_folder = "/app/img"
    date_folder = capture_time.strftime("%Y%m%d")
    save_path = os.path.join(base_folder, date_folder)
    os.makedirs(save_path, exist_ok=True)

    file_path = os.path.join(save_path, filename)

    # Step 4: 儲存圖片
    with open(file_path, "wb") as img_file:
        img_file.write(img_data)

    logger.info(f"Image saved to {file_path}")
    print(f"Image saved to {file_path}")
    return filename
