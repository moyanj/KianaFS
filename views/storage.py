from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

import db
import drivers
import views

router = APIRouter(prefix="/api/storage")


class AddStorage(BaseModel):
    name: str
    driver: str
    driver_settings: dict = {}
    priority: int = 5
    enabled: bool = True

    @field_validator("driver")
    def driver_validator(cls, v):
        if v not in drivers.drivers.keys():
            raise ValueError("Invalid driver")
        return v


@router.post("/add")
async def add_storage(data: AddStorage, _=views.login()):
    try:
        await db.Storage.create(**data.model_dump())
        return views.Response(msg="Storage added successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to add storage")


@router.get("/list")
async def list_storage():
    try:
        storage_list = await db.Storage.all()
        return views.Response(
            [
                {
                    "id": storage.id,
                    "driver": storage.driver,
                    "priority": storage.priority,
                    "enabled": storage.enabled,
                    "name": storage.name,
                }
                for storage in storage_list
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list storage")
