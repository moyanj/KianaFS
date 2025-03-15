from drivers import Driver
import os
import aiowebdav.client
import io


class WebdavDriver(Driver):
    name = "webdav"
    name_human = "Webdav存储"

    setting_define = [
        {
            "name": "Webdav 服务器地址",
            "type": "text",
            "default": "",
            "key": "server",
        },
        {
            "name": "Webdav 服务器用户名",
            "type": "text",
            "default": "",
            "key": "username",
        },
        {
            "name": "Webdav 服务器密码",
            "type": "password",
            "default": "",
            "key": "password",
        },
        {
            "name": "Webdav 服务器根目录",
            "type": "text",
            "default": "/",
            "key": "root",
        },
    ]

    def __init__(self, settings: dict):
        super().__init__(settings)
        self.client = aiowebdav.client.Client(
            {
                "webdav_hostname": self.setting["server"],
                "webdav_login": self.setting["username"],
                "webdav_password": self.setting["password"],
            }
        )

    async def add_chunk(self, data, hash):
        byte_io = io.BytesIO(data)
        await self.client.upload_to(
            byte_io,
            os.path.join(self.setting["root"], hash),
        )
        return True

    async def get_chunk(self, hash):
        byte_io = io.BytesIO()
        await self.client.download_from(
            byte_io,
            os.path.join(self.setting["root"], hash),
        )
        return byte_io.getvalue()

    async def delete_chunk(self, hash):
        await self.client.clean(os.path.join(self.setting["root"], hash))
        return True
