from drivers import Driver
import os
import aioftp


class FTPDriver(Driver):
    name = "ftp"
    name_human = "FTP存储"

    setting_define = [
        {
            "name": "FTP主机",
            "type": "text",
            "default": "",
            "key": "host",
        },
        {
            "name": "FTP端口",
            "type": "number",
            "default": 21,
            "key": "port",
        },
        {
            "name": "FTP用户名",
            "type": "text",
            "default": "",
            "key": "username",
        },
        {
            "name": "FTP密码",
            "type": "password",
            "default": "",
            "key": "password",
        },
        {
            "name": "FTP存储路径",
            "type": "text",
            "default": "/",
            "key": "path",
        },
    ]

    def __init__(self, settings: dict):
        super().__init__(settings)
        self.host = settings["host"]
        self.port = settings["port"]
        self.username = settings["username"]
        self.password = settings["password"]
        self.path = settings["path"]
        self.client = aioftp.Client()

    async def connect(self):
        await self.client.connect(self.host, self.port)
        await self.client.login(self.username, self.password)
        await self.client.change_directory(self.path)

    async def close(self):
        if self.client:
            await self.client.quit()

    async def add_chunk(self, data, hash):
        async with self.client.upload_stream(hash) as stream:  # type: ignore
            await stream.write(data)
        return True

    async def get_chunk(self, hash):
        async with self.client.download_stream(hash) as stream:  # type: ignore
            data = await stream.read()
            return data

    async def delete_chunk(self, hash):
        await self.client.remove(hash)
        return True
