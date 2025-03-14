from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import db
import views
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return views.Response(msg=exc.detail, code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return views.Response(data=exc.errors(), msg="Request is Invalid", code=400)


@app.get("/")
def base_root():
    return "Welcome to KianaFS"


app.mount(
    "/webui",
    StaticFiles(directory="webui/dist", check_dir=False, html=True),
    name="static",
)


@app.get("/api")
def api_root():
    return "Welcome to KianaFS API"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
