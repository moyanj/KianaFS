import dotenv
import json
import os
from typing import Optional

dotenv.load_dotenv()
json_config = json.loads(open("conf.json", "r").read())


def _get_key(key: str, default: Optional[str] = None):
    return json_config.get(key, os.environ.get(key, default))


DB_URL = _get_key("DB_URL", "sqlite://KianaFS.db")
SECRET_KEY = _get_key("SECRET_KEY", "114514")
USE_REDIS = _get_key("USE_REDIS", "false").lower() == "true"
REDIS_HOST = _get_key("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(_get_key("REDIS_PORT", "6379"))
REDIS_DB = int(_get_key("REDIS_DB", "0"))
REDIS_PASSWORD = _get_key("REDIS_PASSWORD", "")
EXPIRE_TIME = int(_get_key("EXPIRE_TIME", "86400"))
MAX_PATH = int(_get_key("MAX_PATH", "8192"))
