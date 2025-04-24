import os
import sqlite3
import time

from config_loader import (
    load_config,
)
from dotenv import load_dotenv
from logger import setup_logger

config = load_config()
logger = setup_logger()

# 載入 .env 檔案
load_dotenv()


class SQLiteHandler:
    def __init__(self, db_path=None):
        """
        初始化 SQLiteHandler 物件
        :param db_path: 資料庫檔案的路徑
        """
        self.db_path = db_path or os.getenv("DBW_SQLITE_PATH")
        if not self.db_path:
            raise ValueError(
                "Database path is not specified in .env or as a parameter."
            )
        self.conn = self.connect()
        self.enable_wal_mode()

    def connect(self):
        """
        建立 SQLite 資料庫連線
        :return: SQLite 連線物件
        """
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            logger.info(f"Connected to SQLite database at {self.db_path}")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error connecting to SQLite database: {e}")
            raise

    def enable_wal_mode(self):
        """
        啟用 Write-Ahead Logging (WAL) 模式
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            logger.info("WAL mode enabled.")
        except sqlite3.Error as e:
            logger.error(f"Error enabling WAL mode: {e}")
            raise

    def execute_query(self, query, params=None, retries=5):
        """
        執行查詢語句
        :param query: SQL 查詢語句
        :param params: 查詢參數 (可選)
        :param retries: 重試次數
        :return: 查詢結果
        """
        for attempt in range(retries):
            try:
                cursor = self.conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.conn.commit()
                return cursor.fetchall()
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    logger.info(
                        f"Database is locked. Retrying {attempt + 1}/{retries}..."
                    )
                    time.sleep(1)  # 等待 1 秒後重試
                else:
                    raise RuntimeError(f"Error executing query: {e}")

    def close(self):
        """
        關閉資料庫連線
        """
        if self.conn:
            self.conn.close()
            logger.info("SQLite connection closed.")


# 使用範例
if __name__ == "__main__":
    db_handler = SQLiteHandler()

    # 插入資料 (範例)
    insert_query = """
    INSERT INTO capture_log (
        capture_datetime,
        img_base64,
        img_path,
        predict_probability) 
    VALUES (?, ?, ?, ?);
    """
    visitor_data = ("2025-04-24T16:44:06.897458", "aLYqcyPpvL", "O1ITbjw0Np", "94.87")
    db_handler.execute_query(insert_query, visitor_data)

    # 查詢資料 (範例)
    select_query = "SELECT * FROM capture_log;"
    results = db_handler.execute_query(select_query)
    for row in results:
        print(row)
