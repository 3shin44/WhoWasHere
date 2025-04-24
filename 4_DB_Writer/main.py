from config_loader import (
    load_config,
)

from logger import setup_logger

from redis_consumer import RedisConsumer
from db_writer import SQLiteHandler
from util import convert_db_item



def main():
    try:
        config = load_config()
        logger = setup_logger()
        logger.info(f"Starting {config['app']['name']} v{config['app']['version']}")

        db_handler = SQLiteHandler()

        consumer = RedisConsumer()

        def custom_callback(item):
            insert_query, params = convert_db_item(item)
            db_handler.execute_query(insert_query, params)

        consumer.listen(callback=custom_callback)
    except Exception as e:
        logger.error(f"Main process error: {e}")
    finally:
        db_handler.close()


if __name__ == "__main__":
    main()
