"""
Slackチャンネル権限取得サービス
users.conversations API でユーザーがアクセス可能なチャンネルIDを取得し
Redisキャッシュと組み合わせてRAGフィルタリングに使用する
"""
import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.services.cache import get_user_channels, set_user_channels

logger = logging.getLogger(__name__)


def get_accessible_channel_ids(user_id: str, slack_client: WebClient) -> list[str]:
    """
    ユーザーがアクセス可能なSlackチャンネルIDリストを返す
    キャッシュヒット時はRedisから、キャッシュミス時はSlack APIから取得する

    Args:
        user_id: SlackユーザーID
        slack_client: Slack WebClient インスタンス

    Returns:
        アクセス可能なチャンネルIDのリスト
    """
    # キャッシュから取得を試みる
    cached = get_user_channels(user_id)
    if cached is not None:
        logger.debug("キャッシュからチャンネルリストを取得しました（user_id=%s）", user_id)
        return cached

    # キャッシュミス → Slack API から取得
    channel_ids: list[str] = []
    try:
        cursor = None
        while True:
            response = slack_client.users_conversations(
                user=user_id,
                types="public_channel,private_channel",
                exclude_archived=True,
                limit=200,
                cursor=cursor,
            )
            channels = response.get("channels", [])
            channel_ids.extend(ch["id"] for ch in channels)

            # ページネーション処理
            next_cursor = response.get("response_metadata", {}).get("next_cursor")
            if not next_cursor:
                break
            cursor = next_cursor

    except SlackApiError as e:
        logger.error("Slack users.conversations APIエラー（user_id=%s）: %s", user_id, e)
        return []

    # Redisにキャッシュして次回以降はAPI不要にする
    set_user_channels(user_id, channel_ids)
    logger.info("チャンネルリストを取得・キャッシュしました（user_id=%s, count=%d）", user_id, len(channel_ids))
    return channel_ids
