"""
Slack履歴フェッチャー
conversations.history API で前日分のメッセージを取得する
チャンネルごとにメッセージをまとめてドキュメント形式に変換する
"""
import logging
import os
import time
from datetime import datetime, timedelta, timezone

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
# 取り込み対象チャンネルID（カンマ区切り環境変数）
TARGET_CHANNEL_IDS = os.environ.get("SLACK_TARGET_CHANNEL_IDS", "").split(",")

_slack_client = WebClient(token=SLACK_BOT_TOKEN)


def fetch_yesterday_messages() -> list[dict]:
    """
    前日のSlackメッセージを対象チャンネルから取得してドキュメントリストに変換する

    Returns:
        ドキュメントリスト（各要素は {"id": str, "content": str, "metadata": dict}）
    """
    now = datetime.now(timezone.utc)
    yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday_start + timedelta(days=1)

    oldest = str(yesterday_start.timestamp())
    latest = str(yesterday_end.timestamp())

    documents: list[dict] = []
    date_str = yesterday_start.strftime("%Y-%m-%d")

    for channel_id in TARGET_CHANNEL_IDS:
        channel_id = channel_id.strip()
        if not channel_id:
            continue

        messages = _fetch_channel_messages(channel_id, oldest, latest)
        if not messages:
            continue

        # チャンネルのメタデータを取得
        is_private = _is_private_channel(channel_id)

        # メッセージを1ドキュメントに結合
        content_lines = []
        for msg in messages:
            user = msg.get("user", "unknown")
            text = msg.get("text", "").strip()
            if text:
                content_lines.append(f"[{user}] {text}")

        if content_lines:
            documents.append({
                "id": f"slack_{channel_id}_{date_str}",
                "content": "\n".join(content_lines),
                "metadata": {
                    "source": "slack",
                    "channel_id": channel_id,
                    "is_private": str(is_private),
                    "date": date_str,
                },
            })

    logger.info("Slackメッセージを取得しました: %d チャンネル分", len(documents))
    return documents


def _fetch_channel_messages(channel_id: str, oldest: str, latest: str) -> list[dict]:
    """チャンネルの指定期間メッセージを取得する（ページネーション対応）"""
    messages: list[dict] = []
    cursor = None

    try:
        while True:
            response = _slack_client.conversations_history(
                channel=channel_id,
                oldest=oldest,
                latest=latest,
                limit=200,
                cursor=cursor,
            )
            messages.extend(response.get("messages", []))

            next_cursor = response.get("response_metadata", {}).get("next_cursor")
            if not next_cursor:
                break
            cursor = next_cursor
            time.sleep(0.5)  # APIレート制限対策

    except SlackApiError as e:
        logger.error("Slack conversations.history APIエラー（channel=%s）: %s", channel_id, e)

    return messages


def _is_private_channel(channel_id: str) -> bool:
    """チャンネルがプライベートかどうかを確認する"""
    try:
        response = _slack_client.conversations_info(channel=channel_id)
        return response["channel"].get("is_private", False)
    except SlackApiError:
        return False
