import json
import os
import base64
from datetime import datetime
import uuid

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
        data.get("img_base64"),
        filename,
        data.get("predict_probability"),
        data.get("class_label")  # 預設為 None，如果沒有提供 note
    )
    return insert_query, params

def save_to_file(item):
    """
    取出BASE64轉為JPG圖檔, 儲存至指定路徑
    """
    data = convert_json(item)  # 將 JSON 字串轉換為字典

    # Decode the BASE64 string
    img_data = base64.b64decode(data.get("img_base64"))

    # Parse the external timestamp
    capture_datetime = data.get("capture_datetime")
    if not capture_datetime:
        logger.error("capture_datetime is missing in the input data.")
        raise ValueError("capture_datetime is missing in the input data.")
    try:
        capture_time = datetime.fromisoformat(capture_datetime)
    except ValueError:
        logger.error("Invalid capture_datetime format. Expected ISO 8601 format.")
        raise ValueError("Invalid capture_datetime format. Expected ISO 8601 format.")

    # Generate timestamp and UUID
    timestamp = capture_time.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Format: YYYYMMDD_HHMMSS_sss
    short_uuid = str(uuid.uuid4())[:5]  # Generate a 5-character UUID

    # Get the label from the input data
    class_label = data.get("class_label", "unknown")  # Default to "unknown" if label is not provided

    # Construct the filename
    filename = f"{timestamp}_{class_label}_{short_uuid}.jpg"

    # Get the base folder from the .env file
    # 固定路徑為容器內的掛載資料夾
    mount_path = "/app/img"
    base_folder = os.path.join(mount_path)
    if not base_folder:
        logger.error("DBW_IMG_FOLDER is not set in the .env file.")
        raise ValueError("DBW_IMG_FOLDER is not set in the .env file.")

    # Create the subfolder for the current date
    date_folder = capture_time.strftime("%Y%m%d")
    save_path = os.path.join(base_folder, date_folder)
    os.makedirs(save_path, exist_ok=True)  # Ensure the folder exists

    # Full file path
    file_path = os.path.join(save_path, filename)

    # Write the image data to the file
    with open(file_path, "wb") as img_file:
        img_file.write(img_data)

    logger.info(f"Image saved to {file_path}")
    print(f"Image saved to {file_path}")
    return filename