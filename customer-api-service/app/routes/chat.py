"""
顧客向けチャットAPIルーター
WordPressのJavaScript Widgetからリクエストを受け付ける
"""
import logging
import time
import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services import rag
from app.services.logger import log_usage
from app.services.recaptcha import verify_recaptcha_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["chat"])


class ChatRequest(BaseModel):
    """チャットリクエストスキーマ"""
    question: str = Field(..., min_length=1, max_length=1000, description="ユーザーの質問")
    recaptcha_token: str = Field(..., description="reCAPTCHA Enterprise トークン")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="セッションID")


class ChatResponse(BaseModel):
    """チャットレスポンススキーマ"""
    answer: str
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    顧客向けFAQ チャットエンドポイント
    reCAPTCHAで検証後、RAGで回答を生成して返す
    """
    # reCAPTCHA検証
    is_human = await verify_recaptcha_token(request.recaptcha_token)
    if not is_human:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="reCAPTCHA検証に失敗しました。",
        )

    # RAGクエリ実行
    start_time = time.time()
    result = rag.query_customer_faq(user_question=request.question)
    latency_ms = int((time.time() - start_time) * 1000)

    # BigQueryにログ記録
    log_usage(
        session_id=request.session_id,
        question=request.question,
        answer=result.answer,
        success=result.success,
        latency_ms=latency_ms,
    )

    return ChatResponse(answer=result.answer, session_id=request.session_id)
