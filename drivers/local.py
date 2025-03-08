from drivers import Driver
import os
import aiofiles


class LocalDriver(Driver):
    name = "local"
    name_human = "本地存储"

    setting_define = [
        {
            "name": "存储路径",
            "type": "text",
            "default": "",
            "key": "path",
        }
    ]

    def __init__(self, settings: dict):
        super().__init__(settings)
        self.path = settings["path"]
        os.makedirs(self.path, exist_ok=True)

    async def add_chunk(self, data, hash):
        async with aiofiles.open(
            os.path.join(self.path, hash),
            "wb",
        ) as f:
            await f.write(data)

    async def get_chunk(self, hash):
        async with aiofiles.open(
            os.path.join(self.path, hash),
            "rb",
        ) as f:
            return await f.read()

    async def delete_chunk(self, hash):
        try:
            os.remove(os.path.join(self.path, hash))
            return True
        except Exception as e:
            return False
