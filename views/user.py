from fastapi import APIRouter
import db
import hashlib

router = APIRouter(prefix="/api/user")


@router.post("/login")
def login(username: str, password: str, hash: bool):
    user = db.User.get(username=username)
