from drivers import Driver
import os
from alist import AList, AListUser, AListFile
import asyncio


class AListDriver(Driver):
    name = "alist"
    name_human = "AList"

    setting_define = [
        {
            "name": "AList 服务器地址",
            "type": "text",
            "default": "",
            "key": "server",
        },
        {
            "name": "AList 服务器用户名",
            "type": "text",
            "default": "",
            "key": "username",
        },
        {
            "name": "AList 服务器密码",
            "type": "password",
            "default": "",
            "key": "password",
        },
        {
            "name": "AList 服务器根目录",
            "type": "text",
            "default": "/",
            "key": "root",
        },
    ]

    def __init__(self, settings: dict):
        super().__init__(settings)
        self.user = AListUser(self.setting["username"], self.setting["password"])
        self.alist = AList(self.setting["server"])
        self.login()

    def login(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.run_until_complete(self.alist.login(self.user))
        else:
            asyncio.run(self.alist.login(self.user))

    async def add_chunk(self, fp, hash):
        return await self.alist.upload(os.path.join(self.setting["root"], hash), fp)

    async def get_chunk(self, hash):
        data = await self.alist.open(os.path.join(self.setting["root"], hash))
        if isinstance(data, AListFile):
            return await data.read()

        raise FileNotFoundError()

    async def delete_chunk(self, hash):
        return await self.alist.remove(os.path.join(self.setting["root"], hash))
