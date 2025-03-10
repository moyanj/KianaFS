from fastapi import APIRouter, HTTPException
import db
import views

router = APIRouter(prefix="/api/chunk")


@router.get("/metadata/<hash>")
async def get_chunk_metadata(hash: str):
    chunk = await db.Chunk.get_or_none(hash=hash)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    await chunk.fetch_related("storages")
    return views.Response(
        {
            "hash": chunk.hash,
            "size": chunk.size,
            "storage": [s.name for s in chunk.storages],
        }
    )


@router.get("/list")
async def list_chunk(page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    chunks = await db.Chunk.all().offset(offset).limit(page_size)
    return views.Response(
        [
            {
                "hash": chunk.hash,
                "size": chunk.size,
                "storage": [s.name for s in chunk.storages],
            }
            for chunk in chunks
        ]
    )


@router.get("/download/<hash>")
async def download(hash: str):
    return await views.get_chunk(hash)
