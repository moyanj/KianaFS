import logging
from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import db
import drivers
import hashlib
import random
from typing import Optional
from urllib.parse import quote

router = APIRouter(prefix="/api/file")


@router.post("/upload")
async def upload(file: UploadFile, filename: Optional[str] = None):
    filename = filename if filename else file.filename

    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # 检查文件是否已存在
    if await db.File.exists(filename=filename):
        raise HTTPException(status_code=400, detail="File already exists")

    # 存储分块到驱动
    storage_list = await db.Storage.filter(enabled=True).all()
    if not storage_list:
        raise HTTPException(status_code=500, detail="No available storage")
    # 提取优先级
    priorities = [item.priority for item in storage_list]
    # 分块处理文件
    chunk_size: int = await db.get_cfg("chunk_size", 1024 * 1024)
    chunks = []
    total_size = 0
    while chunk := await file.read(chunk_size):
        total_size += len(chunk)
        chunk_hash = hashlib.sha1(chunk + filename.encode()).hexdigest()
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
            try:
                await driver.add_chunk(fp=chunk, hash=chunk_hash)
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Failed to add chunk to storage: {str(e)}"
                )

        # 创建 Chunk 实例并保存到数据库
        chunk_instance = await db.Chunk.create(hash=chunk_hash, size=len(chunk) / 1024)

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
            size=total_size / 1024,  # 文件大小以 KB 为单位
        )
        return {"message": "File uploaded successfully", "hash": file_hash}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save file info to database: {str(e)}"
        )


@router.get("/download/{key:path}")
async def download(key: str, path: bool = False):
    if path:
        file = await db.File.get_or_none(filename=key)
    else:
        key = key.split("/")[0]
        file = await db.File.get_or_none(hash=key)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    async def response_data():
        for chunk in file.chunks:
            chunk = await db.Chunk.get_or_none(hash=chunk)
            if not chunk:
                raise Exception("Chunk not found")

            await chunk.fetch_related("storages")
            storage = random.choice(chunk.storages)
            driver = drivers.drivers[storage.driver](storage.driver_settings)  # type: ignore
            try:
                chunk_data = await driver.get_chunk(chunk.hash)
                yield chunk_data
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get chunk from storage: {str(e)}",
                )

    return StreamingResponse(
        response_data(),  # type: ignore
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={quote(file.filename)}",
            "Content-Length": str(int(file.size * 1024)),
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
            raise HTTPException(status_code=404, detail="File not found")

        return {
            "hash": file.hash,
            "filename": file.filename,
            "size": file.size,  # 文件大小以 KB 为单位
            "chunks": file.chunks,  # 存储分块哈希值列表
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get file metadata: {str(e)}"
        )


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
        raise HTTPException(status_code=500, detail=f"Failed to list file: {str(e)}")


@router.delete("/delete/{key:path}")
async def delete_file(key: str, path: bool = False):
    if path:
        file = await db.File.get_or_none(filename=key)
    else:
        key = key.split("/")[0]
        file = await db.File.get_or_none(hash=key)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # 检查每个分块是否被其他文件使用
    for chunk_hash in file.chunks:
        chunk = await db.Chunk.get_or_none(hash=chunk_hash)
        if not chunk:
            continue
        # 如果分块没有被其他文件使用，则删除分块及其存储
        await chunk.fetch_related("storages")
        for storage in chunk.storages:
            driver = drivers.drivers[storage.driver](storage.driver_settings)  # type: ignore
            try:
                await driver.delete_chunk(chunk.hash)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete chunk from storage: {str(e)}",
                )
        await chunk.delete()

    # 删除文件记录
    await file.delete()
    return {"message": "File deleted successfully"}


@router.get("/list/<path:path>")
async def list_file_by_path(path: str):
    if not path.endswith("/"):
        path += "/"

    if path == "/":
        path = ""
    try:
        file_list = await db.File.filter(filename__startswith=path)
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
        raise HTTPException(status_code=500, detail=f"Failed to list file: {str(e)}")
