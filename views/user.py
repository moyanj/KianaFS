from fastapi import APIRouter
import db
import hashlib
import jwt

router = APIRouter(prefix="/api/user")


@router.post("/login")
async def login(username: str, password: str, raw: bool = True):
    user = await db.User.get_or_none(username=username)
    if user is None:
        return {"error": "Invalid username or password"}

    if raw:
        password = hashlib.sha256(password.encode()).hexdigest()

    if user.password == password:
        secret_key = await db.get_cfg("secret_key", "114514")
        token = jwt.encode({"username": username}, secret_key, algorithm="HS256")
        return {"token": token}
    else:
        return {"error": "Invalid username or password"}


@router.post("/register")
async def register(username: str, password: str, raw: bool = True):
    user = await db.User.get_or_none(username=username)
    if user is not None:
        return {"error": "Username already exists"}
    if raw:
        password = hashlib.sha256(password.encode()).hexdigest()

    await db.User.create(username=username, password=password)
    return {"success": True}


@router.get("/info")
async def info(token: str):
    secret_key = await db.get_cfg("secret_key", "114514")
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        username = payload["username"]
        user = await db.User.get_or_none(username=username)
        if user is None:
            return {"error": "Invalid token"}
        return {"username": username, "permission": user.permission}
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
