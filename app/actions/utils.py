import json
from collections import deque
from typing import Any

from aioredis import Redis


async def redis_list(pattern: str, redis: Redis) -> Any:
    return await redis.keys(pattern)


async def redis_fetch(key: str, redis: Redis) -> Any:
    val = await redis.get(key)
    return json.loads(val) if val else None


async def redis_write(key: str, val: Any, redis: Redis) -> None:
    await redis.set(key, json.dumps(val))


async def redis_delete(key: str, redis: Redis) -> None:
    await redis.delete(key)
