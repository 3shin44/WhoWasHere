import redis
from dotenv import load_dotenv
import os

# 載入 .env 檔案
load_dotenv()

class RedisConsumer:
    def __init__(self, redis_host=None, redis_port=None, redis_list=None, timeout=0, redis_password=None):
        """
        初始化 RedisConsumer 物件
        :param redis_host: Redis 伺服器的主機名稱
        :param redis_port: Redis 伺服器的埠號
        :param redis_list: 要監聽的 Redis list 名稱
        :param timeout: blpop 的超時時間，0 表示無限等待
        :param redis_password: Redis 伺服器的密碼
        """
        self.redis_host = redis_host or os.getenv('DBW_REDIS_IP', 'localhost')
        self.redis_port = redis_port or int(os.getenv('DBW_REDIS_PORT', 6379))
        self.redis_list = redis_list or os.getenv('DBW_REDIS_QUEUE', 'default_list')
        self.timeout = timeout or int(os.getenv('DBW_REDIS_BLPOP_TIMEOUT', 5))
        self.redis_password = redis_password or os.getenv('DBW_REDIS_PW', None)
        self.redis_client = redis.StrictRedis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            decode_responses=True
        )

    def listen(self, callback=None):
        """
        開始監聽 Redis list，使用 blpop 模式
        :param callback: 處理資料的 Callback function
        """
        while True:
            # 使用 blpop 從 list 中取出資料
            item = self.redis_client.blpop(self.redis_list, timeout=self.timeout)
            
            if item is None:
                continue  # 如果沒有資料，繼續等待
            
            if callback:
                callback(item)  # 呼叫傳入的 Callback function


# 使用範例
if __name__ == "__main__":
    def custom_callback(item):
        print(f"Custom callback processing item: {item}")

    consumer = RedisConsumer()
    consumer.listen(callback=custom_callback)