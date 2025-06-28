FROM python:3.11-slim

WORKDIR /app

# 安裝 tzdata 並設定時區為 Asia/Taipei
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .