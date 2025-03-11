import db.conf as conf

try:
    import redis.asyncio as redis

    redis_available = True
except ImportError:
    redis_available = False


class CacheMock:
    async def get(self, key: str) -> bytes:
        return b""

    async def set(self, key: str, value: bytes, ex: int = 0) -> None:
        return None


if redis_available:
    cache = redis.Redis(  # type: ignore
        host=conf.REDIS_HOST,
        port=conf.REDIS_PORT,
        db=conf.REDIS_DB,
        password=conf.REDIS_PASSWORD,
    )

else:
    cache = CacheMock()


async def get_cache(key: str):
    return await cache.get(key)


async def set_cache(key: str, value: bytes, ex: int = 0):
    return await cache.set(key, value, ex)
