import json

def convert_db_item(item):
    """
    將資料轉換為 SQLite 插入語法所需的參數
    :param item: Tuple 格式資料，例如 ('visitor_queue', '{"capture_datetime": "...", "img_base64": "...", "img_path": "...", "predict_probability": "..."}')
    :return: SQL 插入語法字串和對應的參數
    """
    try:
        keyname, value = item  # 解構 tuple，取得 keyname 和 JSON 字串
        data = json.loads(value)  # 將 JSON 字串轉換為字典
        insert_query = """
        INSERT INTO capture_log (capture_datetime, img_base64, img_path, predict_probability) 
        VALUES (?, ?, ?, ?);
        """
        params = (
            data.get("capture_datetime"),
            data.get("img_base64"),
            data.get("img_path"),
            data.get("predict_probability"),
        )
        return insert_query, params
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Error converting item: {e}")
        
