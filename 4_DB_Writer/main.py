from config_loader import (
    load_config,
)
from db_writer import SQLiteHandler
from logger import setup_logger
from redis_consumer import RedisConsumer
from util import convert_db_item, save_to_file


def main():
    try:
        config = load_config()
        logger = setup_logger()
        logger.info(f"Starting {config['app']['name']} v{config['app']['version']}")

        db_handler = SQLiteHandler()
        consumer = RedisConsumer()

        def consumer_callback(item):
            file_name = save_to_file(item)  # 儲存圖片並取得檔名
            insert_query, params = convert_db_item(item, file_name)
            db_handler.execute_query(insert_query, params)
            
        consumer.listen(callback=consumer_callback)
    except Exception as e:
        logger.error(f"Main process error: {e}")
    finally:
        db_handler.close()


if __name__ == "__main__":
    main()
