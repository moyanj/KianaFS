import hashlib
from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
import models
import db
import drivers
import random
from contextlib import asynccontextmanager
import traceback
import json


@asynccontextmanager
async def lifespan(app):
    await db.init_db()
    yield
    await db.Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def base_root():
    return "Welcome to DFS"


@app.get("/api")
def api_root():
    return "Welcome to DFS API"


@app.post("/api/storage/add")
async def add_storage(data: models.AddStorage):
    try:
        await db.Storage.create(**data.model_dump())
        return {"message": "Storage added successfully"}
    except Exception as e:
        return {"message": f"Failed to add storage: {str(e)}"}, 500


@app.post("/api/upload")
async def upload(file: UploadFile):
    # 检查文件是否已存在
    if await db.File.exists(filename=file.filename):
        return {"message": "File already exists"}, 400

    # 存储分块到驱动
    storage_list = await db.Storage.filter(enabled=True).all()
    if not storage_list:
        return {"message": "No available storage"}, 500
    # 提取优先级
    priorities = [item.priority for item in storage_list]
    # 分块处理文件
    chunk_size: int = await db.get_cfg("chunk_size", 1024 * 1024)
    chunks = []
    total_size = 0
    while chunk := await file.read(chunk_size):
        total_size += len(chunk)
        chunk_hash = hashlib.sha1(chunk).hexdigest()
        chunks.append(chunk_hash)

        if await db.Chunk.exists(hash=chunk_hash):
            continue
        # 根据优先级选择多个存储驱动
        num_storages = await db.get_cfg("num_storages", 3)
        selected_storages = random.choices(
            storage_list, weights=priorities, k=num_storages
        )

        # 将分块存储到多个驱动
        for storage in selected_storages:
            driver = drivers.drivers[storage.driver](storage.driver_settings)  # type: ignore
            await driver.add_chunk(fp=chunk, hash=chunk_hash)

        # 创建 Chunk 实例并保存到数据库
        chunk_instance = await db.Chunk.create(hash=chunk_hash, size=len(chunk) // 1024)

        # 将 Chunk 与 Storage 关联
        for storage in selected_storages:
            await chunk_instance.storages.add(storage)

    # 保存文件信息到数据库
    try:
        file_hash = hashlib.sha1(str(chunks).encode()).hexdigest()
        await db.File.create(
            hash=file_hash,
            filename=file.filename,
            chunks=chunks,  # 将 chunks 列表转换为 JSON 字符串
            size=total_size // 1024,  # 文件大小以 KB 为单位
        )
        return {"message": "File uploaded successfully", "hash": file_hash}
    except Exception as e:
        traceback.print_exc()
        return {"message": f"Failed to save file info to database: {str(e)}"}, 500


@app.get("/api/download/{hash}")
async def download(hash: str):
    file = await db.File.get_or_none(hash=hash)
    if not file:
        return {"message": "File not found"}, 404

    chunks = await db.Chunk.filter(hash__in=file.chunks).all()

    async def response_data():
        for chunk in chunks:
            await chunk.fetch_related("storages")
            storage = random.choice(chunk.storages)
            driver = drivers.drivers[storage.driver](storage.driver_settings)  # type: ignore
            chunk_data = await driver.get_chunk(chunk.hash)
            yield chunk_data

    return StreamingResponse(
        response_data(),  # type: ignore
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file.filename}",
            "Content-Length": str(file.size * 1024),
        },
    )


@app.get("/api/storage/list")
async def list_storage():
    try:
        storage_list = await db.Storage.all()
        return [
            {
                "id": storage.id,
                "driver": storage.driver,
                "priority": storage.priority,
                "enabled": storage.enabled,
            }
            for storage in storage_list
        ]
    except Exception as e:
        return {"message": f"Failed to list storage: {str(e)}"}, 500


@app.get("/api/file/metadata/{hash}")
async def file_metadata(hash: str):
    try:
        file = await db.File.get_or_none(hash=hash)
        if not file:
            return {"message": "File not found"}, 404

        return {
            "hash": file.hash,
            "filename": file.filename,
            "size": file.size,  # 文件大小以 KB 为单位
            "chunks": file.chunks,  # 存储分块哈希值列表
        }
    except Exception as e:
        return {"message": f"Failed to get file metadata: {str(e)}"}, 500


@app.get("/api/file/list")
async def list_file():
    try:
        file_list = await db.File.all()
        return [
            {
                "hash": file.hash,
                "filename": file.filename,
                "size": file.size,  # 文件大小以 KB 为单位
                "chunks": file.chunks,  # 存储分块哈希值列表
            }
            for file in file_list
        ]
    except Exception as e:
        return {"message": f"Failed to list file: {str(e)}"}, 500


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
