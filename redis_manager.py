from botpy.ext.cog_yaml import read
from botpy import logging
import aioredis
import asyncio
import os

redis_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

# 单例模式（使用装饰器）
def singleton(cls):
    instance = {}

    def wrapper(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return wrapper

@singleton
class redisManager:
    def __init__(self, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self.pool = aioredis.ConnectionPool.from_url(redis_config["redis_url"], max_connections=redis_config["redis_max"])
        self.redis = aioredis.Redis(connection_pool=self.pool)

    async def set_key(self, key, value):
        await self.redis.execute_command("set", key, value)

    async def get_value(self, key):
        value = await self.redis.execute_command("get", key)
        return value

    async def increase_value(self, key):
        # 值自增1
        value = await self.redis.execute_command("incr", key)
        return value

    async def decrease_value(self, key):
        # 值自减1
        value = await self.redis.execute_command("decr", key)
        return value

    async def del_key(self, key):
        await self.redis.execute_command("del", key)

    def __del__(self):
        self._loop.create_task(self.close())

    async def close(self):
        await self.redis.close()


async def test():
    rm = redisManager()
    await rm.set_key("test", 123)
    val = await rm.increase_value("test1")
    # val = await rm.get_value("789")
    print(val)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
