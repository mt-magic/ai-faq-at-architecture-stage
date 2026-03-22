"""
Backlog Wiki取り込みバッチ（Cloud Run Jobs）
Cloud Scheduler から毎日 03:00 に起動される
"""
import logging
import os

from backlog_batch.fetcher import fetch_all_wikis
from common.rag_importer import import_documents

logger = logging.getLogger(__name__)

RAG_CORPUS_NAME = os.environ["INTERNAL_RAG_CORPUS_NAME"]


def run() -> None:
    """Backlog Wiki取り込みバッチのメイン処理"""
    logger.info("Backlog Wiki取り込みバッチを開始します")

    documents = fetch_all_wikis()

    if not documents:
        logger.info("取り込むWiki記事がありませんでした")
        return

    success_count = import_documents(
        corpus_name=RAG_CORPUS_NAME,
        documents=documents,
    )

    logger.info("Backlog Wiki取り込みバッチが完了しました（成功: %d件）", success_count)
