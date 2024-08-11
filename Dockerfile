# 使用官方Python镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录为/app
WORKDIR /app

# 将当前目录下的所有文件复制到容器的/app目录下
COPY . /app

# 安装pip依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口，与FastAPI应用使用的端口一致
EXPOSE 9080

# 定义环境变量
ENV MODULE_NAME="main"
ENV VARIABLE_NAME="app"

# 使用uvicorn运行FastAPI应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9080"]
