from pydantic import BaseModel, field_validator
import drivers


class AddStorage(BaseModel):
    name: str
    driver: str
    driver_settings: dict = {}
    priority: int = 5
    max_size: int = -1
    enabled: bool = True

    @field_validator("driver")
    def driver_validator(cls, v):
        if v not in drivers.drivers.keys():
            raise ValueError("Invalid driver")
        return v
