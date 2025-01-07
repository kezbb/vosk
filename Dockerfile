# 使用官方 Python 运行时作为父镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到容器中
COPY requirements.txt .

# 升级 pip 并安装依赖项，使用阿里云镜像源
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 复制当前目录的内容到容器中的 /app
COPY . .

# 暴露服务端口
EXPOSE 2700

# 启动命令
CMD ["python", "server.py"]
