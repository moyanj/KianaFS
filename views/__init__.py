import db
import drivers
import random
from fastapi.exceptions import HTTPException
from fastapi import Depends, Header, Response as FastapiResponse
import jwt
import orjson
from typing import Any


class Response(FastapiResponse):

    def __init__(
        self,
        data: Any = None,
        msg: str = "OK",
        code: int = 200,
    ):
        d = {
            "msg": msg,
            "success": code == 200,
            "data": data,
            "status_code": code,
        }
        super().__init__(
            content=orjson.dumps(d),
            media_type="application/json",
            status_code=code,
        )


async def get_chunk(hash: str):
    chunk = await db.Chunk.get_or_none(hash=hash)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")

    await chunk.fetch_related("storages")
    if not chunk.storages:
        raise HTTPException(status_code=404, detail="Chunk's storage not found")
    storages: list[db.Storage] = list(chunk.storages)  # 确保 storages 是一个列表
    random.shuffle(storages)  # type: ignore
    for storage in storages:
        try:
            driver = await drivers.get_storage(storage.driver, storage.driver_settings)
            chunk_data = await driver.get_chunk(chunk.hash)
            return chunk_data
        except Exception as e:
            continue
    raise HTTPException(status_code=404, detail="Chunk's storage not found")


async def add_chunk(fp, hash: str, storage_list, num_storages):
    priorities = [item.priority for item in storage_list]

    success_count = 0
    attempts = 0
    max_attempts = num_storages * 2  # 避免无限循环

    # 持续尝试直到满足成功数量或超出尝试次数
    while success_count < num_storages and attempts < max_attempts:
        # 每次随机选择一个存储（允许重复）
        storage = random.choices(storage_list, weights=priorities, k=1)[0]
        driver = await drivers.get_storage(storage.driver, storage.driver_settings)

        try:
            await driver.add_chunk(data=fp, hash=hash)
            success_count += 1
        except Exception as e:
            pass  # 失败时静默继续

        attempts += 1

    # 最终校验成功数量
    if success_count >= num_storages:
        return
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload to {num_storages} storages. Succeeded: {success_count}",
        )


def login():
    async def wrapper(token=Header(None, alias="X-Authorization")):
        if not token:
            raise HTTPException(status_code=401, detail="Token is missing")

        try:
            # 解码并验证 Token
            secret_key = await db.get_cfg("secret_key", "114514")  # type: ignore
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])

            # 校验 payload 是否包含必要字段
            if "username" not in payload:
                raise HTTPException(status_code=401, detail="Invalid token payload")

            # 验证用户是否存在
            user = await db.User.get_or_none(username=payload["username"])
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            elif not user.has_permission("w"):
                raise HTTPException(
                    status_code=403, detail="User does not have permission"
                )

        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Invalid token format")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")

    return Depends(wrapper)
