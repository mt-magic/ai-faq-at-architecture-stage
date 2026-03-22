"""
BigQuery 利用ログサービス
ユーザーの質問・回答・メタデータをBigQueryに記録する
"""
import logging
from datetime import datetime, timezone

from google.cloud import bigquery

from app.config import settings

logger = logging.getLogger(__name__)

_bq_client = bigquery.Client(project=settings.gcp_project_id)
_TABLE_ID = (
    f"{settings.gcp_project_id}"
    f".{settings.bigquery_dataset}"
    f".{settings.bigquery_table}"
)


def log_usage(
    user_id: str,
    user_email: str,
    channel_id: str,
    question: str,
    answer: str,
    success: bool,
    latency_ms: int,
) -> None:
    """
    FAQの利用ログをBigQueryに保存する

    Args:
        user_id: SlackユーザーID
        user_email: ユーザーのメールアドレス
        channel_id: SlackチャンネルID
        question: ユーザーの質問テキスト
        answer: 生成された回答テキスト
        success: RAG処理が成功したかどうか
        latency_ms: 処理時間（ミリ秒）
    """
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "slack-bot",
        "user_id": user_id,
        "user_email": user_email,
        "channel_id": channel_id,
        "question": question,
        "answer": answer,
        "success": success,
        "latency_ms": latency_ms,
    }

    try:
        errors = _bq_client.insert_rows_json(_TABLE_ID, [row])
        if errors:
            logger.error("BigQueryへのログ書き込みエラー: %s", errors)
    except Exception as e:
        # ログ保存の失敗はサービス全体を止めない
        logger.exception("BigQueryログ書き込みに失敗しました: %s", e)
