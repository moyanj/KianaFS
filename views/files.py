import views
from fastapi import APIRouter, UploadFile, HTTPException, Request, Header, Depends
from fastapi.responses import StreamingResponse
import db
import drivers
import hashlib
import aiofiles
import xxhash
from typing import Optional, Annotated
from urllib.parse import quote

router = APIRouter(prefix="/api/file")


async def upload_file(file, filename: str):
    # 检查文件是否已存在
    if await db.File.exists(filename=filename):
        raise HTTPException(status_code=400, detail="File already exists")

    # 获取可用的存储节点列表
    storage_list = await db.Storage.filter(enabled=True).all()
    if not storage_list:
        raise HTTPException(status_code=500, detail="No available storage")

    # 创建 File 实例但不保存到数据库
    file_db = db.File(filename=filename)

    # 获取分块大小配置
    chunk_size: int = await db.get_cfg("chunk_size", 1024 * 1024)
    chunks = []
    total_size = 0
    num_storages = await db.get_cfg("num_storages", 3)
    while chunk := await file.read(chunk_size):
        total_size += len(chunk)
        chunk_hash = xxhash.xxh3_128_hexdigest(chunk)
        chunks.append(chunk_hash)

        # 如果分块已存在，则跳过存储
        if await db.Chunk.exists(hash=chunk_hash):
            continue

        # 将分块存储到多个驱动
        try:
            await views.add_chunk(
                fp=chunk,
                hash=chunk_hash,
                storage_list=storage_list,
                num_storages=num_storages,
            )
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        # 创建 Chunk 实例并保存到数据库
        chunk_instance = await db.Chunk.create(hash=chunk_hash, size=len(chunk) / 1024)

        # 将 Chunk 与 Storage 关联
        for storage in storage_list:
            await chunk_instance.storages.add(storage)

        # 将 Chunk 与 File 关联
        await file_db.chunks.add(chunk_instance)

    # 计算文件哈希值并设置文件大小
    file_hash = xxhash.xxh3_128_hexdigest(str(chunks).encode())
    file_db.hash = file_hash
    file_db.size = total_size / 1024  # 文件大小以 KB 为单位

    # 保存文件信息到数据库
    try:
        await file_db.save()
        return file_hash
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save file info to database: {str(e)}"
        )


@router.post("/upload")
async def upload(
    file: UploadFile,
    filename: Optional[str] = None,
    _=views.login(),
):
    filename = filename if filename else file.filename

    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # 调用 upload_file 函数
    try:
        file_hash = await upload_file(file, filename)
        return {"message": "File uploaded successfully", "hash": file_hash}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/upload/stream")
async def upload_stream(
    x_filename: Annotated[str, Header()],
    request: Request,
    _=views.login(),
):
    file_name = x_filename
    if not file_name:
        raise HTTPException(status_code=400, detail="Filename is required")
    async with aiofiles.tempfile.SpooledTemporaryFile(
        max_size=15 * 1024 * 1024
    ) as temp_file:
        async for chunk in request.stream():
            await temp_file.write(chunk)
        await temp_file.seek(0)
        try:
            file_hash = await upload_file(temp_file, file_name)
            return {"message": "File uploaded successfully", "hash": file_hash}
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/download/{key:path}")
async def download(
    key: str,
    path: bool = False,
):
    if path:
        file = await db.File.get_or_none(filename=key)
    else:
        key = key.split("/")[0]
        file = await db.File.get_or_none(hash=key)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    async def response_data():
        for chunk in file.chunks:
            yield await views.get_chunk(chunk)

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
async def delete_file(key: str, path: bool = False, _=views.login()):
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
