import db
import drivers
import random
from fastapi.exceptions import HTTPException


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
            driver = drivers.drivers[storage.driver](storage.driver_settings)  # type: ignore
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
        driver = drivers.drivers[storage.driver](storage.driver_settings)  # type: ignore

        try:
            await driver.add_chunk(fp=fp, hash=hash)
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
