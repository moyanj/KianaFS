# 使用 Python 3.13 的基础镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装 uv 并清理缓存
RUN pip install --no-cache-dir uv && \
    rm -rf /root/.cache/pip

# 复制依赖声明文件
COPY pyproject.toml uv.lock ./

# 安装核心依赖及指定扩展（按需修改 extras）
RUN uv sync \
    --all-extras

# 复制应用代码
COPY . .

# 暴露应用端口
EXPOSE 23901

# 运行命令（示例使用 uvicorn，按需修改）
CMD ["python", "main.py", "start"]