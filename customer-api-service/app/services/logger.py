"""
BigQuery 利用ログサービス（顧客向け）
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
    session_id: str,
    question: str,
    answer: str,
    success: bool,
    latency_ms: int,
) -> None:
    """
    顧客FAQの利用ログをBigQueryに保存する

    Args:
        session_id: セッションID（個人特定不可の匿名ID）
        question: ユーザーの質問テキスト
        answer: 生成された回答テキスト
        success: RAG処理が成功したかどうか
        latency_ms: 処理時間（ミリ秒）
    """
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "customer-api",
        "session_id": session_id,
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
        logger.exception("BigQueryログ書き込みに失敗しました: %s", e)
