from tortoise import fields, Tortoise
from tortoise.models import Model
from typing import Any

try:
    import orjson as json
except ImportError:
    import orjson as json


class StrJSONField(fields.TextField):  # 将 CharField 改为 TextField
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python_value(self, value):
        try:
            return json.loads(value)  # 尝试解析为 JSON
        except json.JSONDecodeError:
            return value

    def to_db_value(self, value, instance):
        # 如果值是字典或列表，转换为 JSON 字符串；否则直接存储
        v = json.dumps(value)
        if isinstance(v, bytes):
            return v.decode("utf-8")
        else:
            return v


class Config(Model):
    key = fields.CharField(max_length=255, unique=True, index=True)  # 配置键
    value: Any = StrJSONField()  # 配置值，使用 JSONField 存储结构化数据

    class Meta:  # type: ignore
        db_table = "config"  # 明确指定表名

    def __str__(self):
        return f"{self.key}: {self.value}"


class Storage(Model):
    id = fields.IntField(pk=True, auto_increment=True, generated=True)  # 存储节点 ID
    name = fields.CharField(max_length=255, unique=True, index=True)  # 存储节点名称
    driver = fields.CharField(max_length=255)  # 存储驱动类型
    priority = fields.SmallIntField(index=True)  # 优先级，用于选择存储节点
    enabled = fields.BooleanField(default=True)  # 是否启用
    driver_settings = fields.JSONField()  # 驱动设置，使用 JSONField 存储结构化数据

    class Meta:  # type: ignore
        db_table = "storage"

    def __str__(self):
        return f"{self.name} ({self.driver})"


class File(Model):
    hash = fields.CharField(max_length=40, unique=True, pk=True)  # 文件哈希值 (SHA1)
    filename = fields.CharField(max_length=8192, unique=True)  # 文件名
    chunks = fields.ManyToManyField("models.Chunk")  # 多对多关系，关联到Chunk模型
    size = fields.FloatField()  # 文件大小 (KB)
    update_time = fields.DatetimeField(auto_now=True)  # 更新时间

    class Meta:  # type: ignore
        db_table = "file"

    def __str__(self):
        return f"{self.filename} ({self.size} KB)"


class Chunk(Model):
    hash = fields.CharField(max_length=40, unique=True, pk=True)  # 文件块哈希值 (SHA1)
    size = fields.FloatField()  # 文件块大小 (KB)
    storages = fields.ManyToManyField("models.Storage")  # 多对多关系，关联到Storage模型
    update_time = fields.DatetimeField(auto_now=True)  # 更新时间

    class Meta:  # type: ignore
        db_table = "chunk"

    def __str__(self):
        return f"{self.hash} ({self.size} KB)"


class User(Model):
    id = fields.IntField(pk=True, auto_increment=True, generated=True, index=True)
    username = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=80)
    permission = fields.CharField(max_length=16)
    create_time = fields.DatetimeField(auto_now_add=True)

    class Meta:  # type: ignore
        db_table = "user"

    def __str__(self):
        return f"{self.username} ({self.permission})"

    def check_password(self, password):
        return self.password == password

    def has_permission(self, permission):
        return permission in self.permission
