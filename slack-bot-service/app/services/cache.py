"""
Cloud Memorystore (Redis) キャッシュサービス
Slackチャンネル権限情報をキャッシュして、APIコール数を削減する
"""
import json
import logging

import redis

from app.config import settings

logger = logging.getLogger(__name__)

# Redis クライアント（起動時に1度だけ接続）
_redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)

# キャッシュキープレフィックス
CHANNEL_CACHE_PREFIX = "slack:channels:"


def get_user_channels(user_id: str) -> list[str] | None:
    """
    ユーザーがアクセス可能なチャンネルIDリストをキャッシュから取得する

    Args:
        user_id: SlackユーザーID

    Returns:
        チャンネルIDリスト（キャッシュミスの場合はNone）
    """
    try:
        cache_key = f"{CHANNEL_CACHE_PREFIX}{user_id}"
        cached = _redis_client.get(cache_key)
        if cached is None:
            return None
        return json.loads(cached)
    except Exception as e:
        logger.warning("Redisキャッシュ読み取りに失敗しました（user_id=%s）: %s", user_id, e)
        return None


def set_user_channels(user_id: str, channel_ids: list[str]) -> None:
    """
    ユーザーのアクセス可能チャンネルIDリストをキャッシュに保存する

    Args:
        user_id: SlackユーザーID
        channel_ids: チャンネルIDリスト
    """
    try:
        cache_key = f"{CHANNEL_CACHE_PREFIX}{user_id}"
        _redis_client.setex(
            name=cache_key,
            time=settings.redis_ttl_seconds,
            value=json.dumps(channel_ids),
        )
    except Exception as e:
        logger.warning("Redisキャッシュ書き込みに失敗しました（user_id=%s）: %s", user_id, e)


def invalidate_user_channels(user_id: str) -> None:
    """
    ユーザーのチャンネルキャッシュを即時削除する
    Slack Events API（member_joined_channel / member_left_channel）受信時に呼び出す

    Args:
        user_id: SlackユーザーID
    """
    try:
        cache_key = f"{CHANNEL_CACHE_PREFIX}{user_id}"
        _redis_client.delete(cache_key)
        logger.info("チャンネルキャッシュを削除しました（user_id=%s）", user_id)
    except Exception as e:
        logger.warning("Redisキャッシュ削除に失敗しました（user_id=%s）: %s", user_id, e)
