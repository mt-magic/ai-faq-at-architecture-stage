"""
Slack履歴取り込みバッチ（Cloud Run Jobs）
Cloud Scheduler から毎日 02:00 に起動される
"""
import logging
import os

from common.rag_importer import import_documents
from slack_batch.fetcher import fetch_yesterday_messages

logger = logging.getLogger(__name__)

RAG_CORPUS_NAME = os.environ["INTERNAL_RAG_CORPUS_NAME"]


def run() -> None:
    """Slack履歴取り込みバッチのメイン処理"""
    logger.info("Slack履歴取り込みバッチを開始します")

    # 前日のSlackメッセージを取得
    documents = fetch_yesterday_messages()

    if not documents:
        logger.info("取り込むメッセージがありませんでした")
        return

    # RAGコーパスにインポート
    success_count = import_documents(
        corpus_name=RAG_CORPUS_NAME,
        documents=documents,
    )

    logger.info("Slack履歴取り込みバッチが完了しました（成功: %d件）", success_count)
