"""
reCAPTCHA Enterprise 検証サービス
顧客APIへのリクエストがボットでないかを検証する
"""
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

RECAPTCHA_VERIFY_URL = (
    "https://recaptchaenterprise.googleapis.com/v1"
    "/projects/{project_id}/assessments"
)

# reCAPTCHAスコア閾値（0.0〜1.0、高いほど人間らしい）
SCORE_THRESHOLD = 0.5


async def verify_recaptcha_token(token: str) -> bool:
    """
    reCAPTCHA Enterprise でトークンを検証する

    Args:
        token: フロントエンドから送信されたreCAPTCHAトークン

    Returns:
        検証が通った（人間判定）場合はTrue、ボット疑いの場合はFalse
    """
    url = RECAPTCHA_VERIFY_URL.format(project_id=settings.recaptcha_project_id)
    payload = {
        "event": {
            "token": token,
            "siteKey": settings.recaptcha_site_key,
            "expectedAction": "CHAT_SUBMIT",
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=5.0)
            response.raise_for_status()
            data = response.json()

        score: float = data.get("riskAnalysis", {}).get("score", 0.0)
        logger.debug("reCAPTCHAスコア: %.2f", score)
        return score >= SCORE_THRESHOLD

    except Exception as e:
        logger.error("reCAPTCHA検証エラー: %s", e)
        # 検証エラー時は安全側に倒してFalseを返す
        return False
