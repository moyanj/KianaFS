from tortoise import Tortoise
import os
from .schema import *
import secrets
from typing import Any, Coroutine


async def init_db():
    await Tortoise.init(
        db_url=os.environ.get("DB_URL", "sqlite://KianaFS.db"),
        modules={"models": ["db.schema"]},  # 替换为你的模块名
    )
    await Tortoise.generate_schemas()

    if await Config.get_or_none(key="init") is None:
        await Config.create(key="init", value=True)
        await Config.create(key="chunk_size", value=1024 * 1024)
        await Config.create(key="num_storages", value=3)

        admin_pwd = secrets.token_hex(8)
        print(f"admin password: {admin_pwd}")
        await User.create(username="admin", password=admin_pwd, permission="rwa")


async def get_cfg(key: str, default: Any = None):
    val = await Config.get_or_none(key=key)
    if val is None:
        return default
    else:
        return val.value


async def set_cfg(key: str, value):
    val = await Config.get_or_none(key=key)
    if val is None:
        await Config.create(key=key, value=value)
    else:
        val.value = value
        await val.save()


async def exists(table, key: str):
    val = await table.get_or_none(key=key)
    if val is None:
        return False
    else:
        return True
