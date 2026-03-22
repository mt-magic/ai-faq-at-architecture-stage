"""
Customer API Service エントリポイント
顧客向けWordPress ChatウィジェットからのリクエストをFastAPIで処理する
reCAPTCHA Enterprise でボット対策を行いVertex AI RAGで回答を生成する
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.chat import router as chat_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="AI FAQ Customer API Service", version="1.0.0")

# CORSミドルウェア設定（WordPressサイトからのみアクセス許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

app.include_router(chat_router)


@app.get("/health")
def health_check() -> dict:
    """Cloud Run ヘルスチェックエンドポイント"""
    return {"status": "ok"}
