"""
Slack Bolt イベントハンドラー定義
app_mention イベントと member_joined/left_channel イベントを処理する
"""
import logging
import time

from slack_bolt import App

from app.config import settings
from app.services import cache, rag, slack_channels
from app.services.logger import log_usage

logger = logging.getLogger(__name__)


def register_handlers(app: App) -> None:
    """
    Slack Bolt App にイベントハンドラーを登録する

    Args:
        app: Slack Bolt App インスタンス
    """

    @app.event("app_mention")
    def handle_app_mention(event: dict, say, client) -> None:
        """
        @メンションを受け取ったときにRAGで回答を生成して返信する
        """
        user_id = event.get("user", "unknown")
        channel_id = event.get("channel", "")
        thread_ts = event.get("thread_ts") or event.get("ts")

        # メンション部分（<@BOT_ID>）を除去して質問テキストを取得
        raw_text: str = event.get("text", "")
        question = raw_text.split(">", 1)[-1].strip() if ">" in raw_text else raw_text.strip()

        if not question:
            say(text="質問内容が見つかりませんでした。もう一度お試しください。", thread_ts=thread_ts)
            return

        # 「処理中」メッセージを先に送信してUXを改善
        say(text=":loading: 回答を生成中です...", thread_ts=thread_ts)

        # ユーザーがアクセス可能なチャンネルIDを取得（キャッシュ利用）
        accessible_channels = slack_channels.get_accessible_channel_ids(user_id, client)

        # ユーザーメールアドレスを取得
        user_email = ""
        try:
            user_info = client.users_info(user=user_id)
            user_email = user_info["user"]["profile"].get("email", "")
        except Exception:
            pass

        # RAGクエリ実行
        start_time = time.time()
        result = rag.query_internal_faq(
            user_question=question,
            channel_filter=accessible_channels if accessible_channels else None,
        )
        latency_ms = int((time.time() - start_time) * 1000)

        # 回答を送信
        say(text=result.answer, thread_ts=thread_ts)

        # BigQueryにログを記録
        log_usage(
            user_id=user_id,
            user_email=user_email,
            channel_id=channel_id,
            question=question,
            answer=result.answer,
            success=result.success,
            latency_ms=latency_ms,
        )

    @app.event("member_joined_channel")
    def handle_member_joined(event: dict) -> None:
        """
        メンバーがチャンネルに参加したときにキャッシュを即時削除する
        """
        user_id = event.get("user")
        if user_id:
            cache.invalidate_user_channels(user_id)

    @app.event("member_left_channel")
    def handle_member_left(event: dict) -> None:
        """
        メンバーがチャンネルを退出したときにキャッシュを即時削除する
        """
        user_id = event.get("user")
        if user_id:
            cache.invalidate_user_channels(user_id)
