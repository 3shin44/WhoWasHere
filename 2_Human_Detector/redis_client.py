import os

import redis
from dotenv import load_dotenv


class RedisClient:
    def __init__(self, host=None, port=None, db=0, password=None):
        """
        Initialize the Redis client.

        :param host: Redis server host.
        :param port: Redis server port.
        :param db: Redis database number.
        :param password: Redis server password.
        """
        # Load .env file
        load_dotenv()
        host = host or os.getenv("HD_REDIS_IP")
        port = port or int(os.getenv("HD_REDIS_PORT"))
        password = password or os.getenv("HD_REDIS_PW")

        self.client = redis.StrictRedis(host=host, port=port, db=db, password=password)

    def write_to_list(self, list_name, value, ttl=None):
        """
        Write a value to a Redis list and optionally set its expiration time.

        :param list_name: The name of the Redis list.
        :param value: The value to append to the list.
        :param ttl: Time-to-live for the list in seconds (optional).
        """
        try:
            self.client.rpush(list_name, value)
            if ttl:
                self.client.expire(list_name, ttl)
        except redis.RedisError as e:
            raise RuntimeError(f"Error writing to list '{list_name}': {e}")


if __name__ == "__main__":
    import json
    import random
    import string
    import time
    from datetime import datetime

    # Load .env file
    load_dotenv()
    list_name = os.getenv("HD_REDIS_QUEUE")
    redis_client = RedisClient()

    try:

        for i in range(5):
            # Generate JSON value
            json_value = {
                "capture_datetime": datetime.now().isoformat(),  # ISO 8601 format
                "img_base64": "".join(
                    random.choices(string.ascii_letters + string.digits, k=30)
                ),
                "predict_probability": f"{random.uniform(0, 100):.2f}",
                "class_label": "test",
            }
            redis_client.write_to_list(list_name, json.dumps(json_value), ttl=60)
            time.sleep(1)

    except RuntimeError as e:
        print(f"Caught an error: {e}")
