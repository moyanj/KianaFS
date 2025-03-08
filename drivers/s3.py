from drivers import Driver
import aiohttp
import os
import io
import miniopy_async


class S3Driver(Driver):
    name = "s3"
    name_human = "S3"

    setting_define = [
        {
            "name": "AWS访问密钥ID",
            "type": "text",
            "default": "",
            "key": "aws_access_key_id",
        },
        {
            "name": "AWS秘密访问密钥",
            "type": "password",
            "default": "",
            "key": "aws_secret_access_key",
        },
        {
            "name": "S3存储桶名称",
            "type": "text",
            "default": "",
            "key": "bucket_name",
        },
        {
            "name": "S3存储桶根目录",
            "type": "text",
            "default": "/",
            "key": "root",
        },
        {
            "name": "S3服务地址",
            "type": "text",
            "default": "https://s3.amazonaws.com",
            "key": "s3_endpoint_url",
        },
    ]

    def __init__(self, settings: dict):
        super().__init__(settings)
        self.session = miniopy_async.Minio(
            endpoint=self.setting["s3_endpoint_url"],
            access_key=self.setting["aws_access_key_id"],
            secret_key=self.setting["aws_secret_access_key"],
        )
        self.bucket_name = self.setting["bucket_name"]
        self.root = self.setting["root"]

    async def add_chunk(self, data: bytes, hash: str):
        # 上传文件到S3
        key = os.path.join(self.root, hash)
        fp = io.BytesIO(data)
        await self.session.put_object(
            bucket_name=self.bucket_name, object_name=key, data=fp, length=len(data)
        )
        return True

    async def get_chunk(self, hash):
        # 从S3下载文件
        key = os.path.join(self.root, hash)
        async with aiohttp.ClientSession() as session:
            response = await self.session.get_object(self.bucket_name, key, session)
            return await response.read()

    async def delete_chunk(self, hash):
        # 删除S3中的文件
        key = os.path.join(self.root, hash)
        await self.session.remove_object(self.bucket_name, key)
