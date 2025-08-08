FROM python:3.11-slim

# 设置时区和基本依赖
ENV TZ=Asia/Shanghai

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpoppler-cpp-dev \
    libtesseract-dev \
        libzbar0 \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖列表
COPY requirements.txt ./

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && rm -rf /var/lib/apt/lists/*

# 拷贝项目源代码
COPY . .

# 暴露端口
EXPOSE 8081

# 启动命令（可根据实际项目替换）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
