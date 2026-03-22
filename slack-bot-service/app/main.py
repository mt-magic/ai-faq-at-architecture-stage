"""
Slack Bot Service エントリポイント
FastAPI + Slack Bolt (HTTP モード) で Slack Events API を受け付ける
IAP はこのサービスの前段で処理されるため、ここでは Signing Secret 検証のみ行う
"""
import logging

from fastapi import FastAPI, Request, Response
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from app.config import settings
from app.routes.slack import register_handlers

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# Slack Bolt App 初期化（Signing Secret でリクエスト検証）
bolt_app = App(
    token=settings.slack_bot_token,
    signing_secret=settings.slack_signing_secret,
)

# イベントハンドラーを登録
register_handlers(bolt_app)

# FastAPI App 初期化
app = FastAPI(title="AI FAQ Slack Bot Service", version="1.0.0")
handler = SlackRequestHandler(bolt_app)


@app.get("/health")
def health_check() -> dict:
    """Cloud Run ヘルスチェックエンドポイント"""
    return {"status": "ok"}


@app.post("/slack/events")
async def slack_events(req: Request) -> Response:
    """
    Slack Events API からのリクエストを受け付けるエンドポイント
    Slack Bolt が Signing Secret を検証してイベントを処理する
    """
    return await handler.handle(req)
