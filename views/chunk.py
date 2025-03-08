from fastapi import APIRouter, HTTPException
import db
import drivers

router = APIRouter(prefix="/api/chunk")


@router.get("/metadata/<hash>")
async def get_chunk_metadata(hash: str):
    chunk = await db.Chunk.get_or_none(hash=hash)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    await chunk.fetch_related("storages")
    return {
        "hash": chunk.hash,
        "size": chunk.size,
        "storage": [s.name for s in chunk.storages],
    }


@router.get("/list")
async def list_chunk(page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    chunks = await db.Chunk.all().offset(offset).limit(page_size)
    return [
        {
            "hash": chunk.hash,
            "size": chunk.size,
            "storage": [s.name for s in chunk.storages],
        }
        for chunk in chunks
    ]


@router.get("/download/<hash>")
async def download(hash: str):
    chunk = await db.Chunk.get_or_none(hash=hash)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    await chunk.fetch_related("storages")
    for storage in chunk.storages:
        try:
            driver = drivers.drivers[storage.driver](storage.driver_settings)
            return driver.get_chunk(chunk.hash)
        except Exception as e:
            continue
    raise HTTPException(status_code=500, detail="Failed to download chunk")
