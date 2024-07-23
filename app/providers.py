import logging

from arctic import Arctic
from arctic.tickstore import tickstore

from aioredis import create_redis_pool
from aioredis import Redis

from app import settings

store = Arctic(settings.MONGO_HOST)
store.initialize_library(settings.TSDB_NAME, tickstore.TICK_STORE_TYPE)
tsdb = store[settings.TSDB_NAME]


class RedisConnection:
    __redis_instance: Redis = None

    @staticmethod
    async def create_connection():
        if not RedisConnection.__redis_instance:
            logging.info("Creating new redis instance")
            RedisConnection.__redis_instance = await create_redis_pool(
                settings.REDIS_URI
            )
        return RedisConnection.__redis_instance

    @staticmethod
    async def close_connection():
        if RedisConnection.__redis_instance:
            logging.info("Closing redis instance")
            RedisConnection.__redis_instance.close()
            await RedisConnection.__redis_instance.wait_closed()
        RedisConnection.__redis_instance = None
