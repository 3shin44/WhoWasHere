FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝 tzdata 並設定時區為 Asia/Taipei
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 複製 requirements 並安裝套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製其餘程式碼
COPY . .
