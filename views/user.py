from fastapi import APIRouter, HTTPException, Body
import db
import views
import hashlib
import jwt
from pydantic import BaseModel

router = APIRouter(prefix="/api/user")


class Login(BaseModel):
    username: str
    password: str
    raw: bool = True


@router.post("/login")
async def login(u: Login):
    user = await db.User.get_or_none(username=u.username)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if u.raw:
        password = hashlib.sha256(u.password.encode()).hexdigest()
    else:
        password = u.password

    if user.password == password:
        secret_key = await db.get_cfg("secret_key", "114514")
        token = jwt.encode({"username": u.username}, secret_key, algorithm="HS256")
        return views.Response(token)
    else:
        raise HTTPException(status_code=400, detail="Invalid username or password")


@router.post("/register")
async def register(username: str, password: str, raw: bool = True, _=views.login()):
    user = await db.User.get_or_none(username=username)
    if user is not None:
        raise HTTPException(status_code=400, detail="Username already exists")
    if raw:
        password = hashlib.sha256(password.encode()).hexdigest()

    await db.User.create(username=username, password=password)
    return views.Response()


@router.get("/info")
async def info(token: str):
    secret_key = await db.get_cfg("secret_key", "114514")
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        username = payload["username"]
        user = await db.User.get_or_none(username=username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return views.Response({"username": username, "permission": user.permission})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
