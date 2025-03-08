from fastapi import FastAPI
from contextlib import asynccontextmanager

import db
from views.files import router as files_router
from views.storage import router as storage_router
from views.chunk import router as chunk_router
from views.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    app.include_router(files_router)
    app.include_router(storage_router)
    app.include_router(chunk_router)
    app.include_router(user_router)
    yield
    await db.Tortoise.close_connections()


app = FastAPI(lifespan=lifespan, title="KianaFS API")


@app.get("/")
def base_root():
    return "Welcome to KianaFS"


@app.get("/api")
def api_root():
    return "Welcome to KianaFS API"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
