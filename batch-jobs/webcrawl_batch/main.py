"""
WordPressクロール取り込みバッチ（Cloud Run Jobs）
Cloud Scheduler から週次（月曜 04:00）に起動される
"""
import logging
import os

from common.rag_importer import import_documents
from webcrawl_batch.crawler import crawl_wordpress_pages

logger = logging.getLogger(__name__)

RAG_CORPUS_NAME = os.environ["CUSTOMER_RAG_CORPUS_NAME"]


def run() -> None:
    """WordPressクロール取り込みバッチのメイン処理"""
    logger.info("WordPressクロール取り込みバッチを開始します")

    documents = crawl_wordpress_pages()

    if not documents:
        logger.info("取り込むページがありませんでした")
        return

    success_count = import_documents(
        corpus_name=RAG_CORPUS_NAME,
        documents=documents,
    )

    logger.info("WordPressクロール取り込みバッチが完了しました（成功: %d件）", success_count)
