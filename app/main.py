from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
import yt_dlp as youtube_dl
import uuid
import os
import logging
from datetime import datetime

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーションの作成
app = FastAPI(
    title="YouTube Downloader API",
    description="Download YouTube videos and audio using FastAPI",
    version="1.0.0"
)

# ダウンロードディレクトリの設定
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/app/downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class DownloadRequest(BaseModel):
    url: HttpUrl
    download_type: str  # 'audio' または 'video'
    quality: Optional[str] = None  # 例: 'best', 'worst', '720p', '480p'

    class Config:
        schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "download_type": "video",
                "quality": "720"
            }
        }

def clean_old_files():
    """古いダウンロードファイルを削除する（24時間以上経過したファイル）"""
    current_time = datetime.now().timestamp()
    for filename in os.listdir(DOWNLOAD_DIR):
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.isfile(filepath):
            file_time = os.path.getctime(filepath)
            if current_time - file_time > 86400:  # 24時間
                try:
                    os.remove(filepath)
                    logger.info(f"Removed old file: {filename}")
                except Exception as e:
                    logger.error(f"Error removing file {filename}: {e}")

@app.post("/download", response_description="Returns the downloaded file information")
async def download_video(request: DownloadRequest):
    """
    YouTubeの動画または音声をダウンロードするエンドポイント
    """
    # 古いファイルのクリーンアップ
    clean_old_files()

    # ダウンロードタイプの検証
    if request.download_type not in ['audio', 'video']:
        raise HTTPException(
            status_code=400,
            detail="download_type must be 'audio' or 'video'"
        )

    # 一意のファイル名を生成
    unique_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f"{unique_id}.%(ext)s")

    # youtube-dlのオプションを設定
    ydl_opts = {
        'outtmpl': output_template,
        'quiet': False,  # Enable output for better debugging
        'no_warnings': False,  # Enable warnings
        'verbose': True,  # Add verbose output
        'extract_flat': True,  # Add this to help with extraction issues
        'force_generic_extractor': False,  # Don't force generic extractor
        'ignoreerrors': True,  # Continue on download errors
    }

    try:
        if request.download_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            format_string = 'bestvideo+bestaudio/best'
            if request.quality:
                if request.quality.isdigit():
                    format_string = f'bestvideo[height<={request.quality}]+bestaudio/best[height<={request.quality}]'
                else:
                    format_string = request.quality
            ydl_opts.update({'format': format_string})

        logger.info(f"Starting download for URL: {request.url} with options: {ydl_opts}")
        
        # Add error handling for video info extraction
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                # First try to extract video info
                video_info = ydl.extract_info(str(request.url), download=False)
                if not video_info:
                    raise HTTPException(
                        status_code=400,
                        detail="Could not extract video information"
                    )
                
                # If info extraction succeeds, proceed with download
                ydl.download([str(request.url)])
            except youtube_dl.utils.DownloadError as e:
                logger.error(f"Download error details: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Download failed: {str(e)}"
                )

        # ダウンロードされたファイルを検索
        downloaded_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(unique_id)]
        if not downloaded_files:
            raise HTTPException(
                status_code=500,
                detail="Failed to download the file"
            )

        filename = downloaded_files[0]
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/octet-stream'
        )

    except youtube_dl.DownloadError as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"} 
