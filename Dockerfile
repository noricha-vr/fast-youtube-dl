FROM python:3.9-slim

# システムの依存関係をインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# yt-dlpを直接インストール
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp && \
    ln -s /usr/local/bin/yt-dlp /usr/local/bin/youtube-dl

# Pythonの依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY ./app /app

# ダウンロードディレクトリを作成
RUN mkdir -p /app/downloads

# 実行権限を設定
RUN chmod -R 755 /app

# アプリケーションを起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
