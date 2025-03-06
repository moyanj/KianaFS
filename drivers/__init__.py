import os
import importlib
from typing import Any, Dict, List, Tuple, Optional, Generator


class Driver:
    name: str
    name_human: str
    setting_define: List[Dict[str, Any]] = []

    def __init__(self, settings: Dict[str, Any]):
        self.setting = settings

        if self.name is None or self.name_human is None:
            raise ValueError("name and name_human must be set in the driver class")

    async def add_chunk(self, fp, hash):
        raise NotImplementedError(
            "add_chunk method must be implemented in the driver class"
        )

    async def get_chunk(self, hash: str) -> Optional[bytes]:
        raise NotImplementedError(
            "get_chunk method must be implemented in the driver class"
        )

    async def delete_chunk(self, hash: str):
        raise NotImplementedError(
            "delete_chunk method must be implemented in the driver class"
        )

    def __repr__(self) -> str:
        """
        返回存储模块的字符串表示。
        """
        return f"<Driver name={self.name}, name_human={self.name_human}>"


def load_driver() -> Generator[type[Driver]]:
    """
    动态加载当前目录下的所有存储驱动。

    :return: 存储模块列表，每个元素为 (Driver 实例, 模块名称)
    """
    current_dir = os.path.dirname(__file__)

    for file in os.listdir(current_dir):
        if file.endswith(".py") and file != "__init__.py" and "__pycache__" not in file:
            module_name = file[:-3]
            try:
                # 动态导入模块
                module = importlib.import_module(f"{__name__}.{module_name}")
                # 获取所有对象
                for obj in module.__dict__.values():
                    try:
                        if issubclass(obj, Driver) and obj is not Driver:
                            yield obj
                    except TypeError:
                        pass
            except ImportError as e:
                print(f"Failed to load module {module_name}: {e}")
                exit()


drivers = {storager.name: storager for storager in load_driver()}

# 导出公共接口
__all__ = ["drivers"]
