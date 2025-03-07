from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse
import db
import drivers
import hashlib
import random
from typing import Optional

router = APIRouter(prefix="/api/file")


@router.post("/upload")  # 修改为 POST 请求，因为上传文件通常使用 POST 方法
async def upload(
    file: UploadFile, filename: Optional[str] = None
):  # 添加 filename 参数
    # 检查文件是否已存在
    if await db.File.exists(filename=filename if filename else file.filename):
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
            filename=(
                filename if filename else file.filename
            ),  # 使用 filename 参数或文件本身的文件名
            chunks=chunks,  # 将 chunks 列表转换为 JSON 字符串
            size=total_size // 1024,  # 文件大小以 KB 为单位
        )
        return {"message": "File uploaded successfully", "hash": file_hash}
    except Exception as e:
        return {"message": f"Failed to save file info to database: {str(e)}"}, 500


@router.get("/download/{key:path}")
async def download(key: str, path: bool = False):
    if path:
        file = await db.File.get_or_none(filename=key)
    else:
        key = key.split("/")[0]
        file = await db.File.get_or_none(hash=key)
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


@router.get("/metadata/{key:path}")
async def file_metadata(key: str, path: bool = False):

    try:
        if path:
            file = await db.File.get_or_none(filename=key)
        else:
            key = key.split("/")[0]
            file = await db.File.get_or_none(hash=key)
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


@router.get("/list")
async def list_file(page: int = 1, page_size: int = 10):
    try:
        offset = (page - 1) * page_size
        file_list = await db.File.all().offset(offset).limit(page_size)
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
