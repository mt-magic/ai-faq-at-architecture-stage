"""
Vertex AI RAG Engine インポーター（共通）
各バッチから生成されたドキュメントをRAGコーパスにアップロードする
"""
import logging
import os
import tempfile

import vertexai
from vertexai.preview import rag

logger = logging.getLogger(__name__)

GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
GCP_LOCATION = os.environ.get("GCP_LOCATION", "asia-northeast1")

vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)


def import_documents(
    corpus_name: str,
    documents: list[dict],
) -> int:
    """
    ドキュメントリストをRAGコーパスにインポートする

    Args:
        corpus_name: RAGコーパスのリソース名
        documents: ドキュメントのリスト。各要素は {"id": str, "content": str, "metadata": dict}

    Returns:
        インポートに成功したドキュメント数
    """
    if not documents:
        logger.warning("インポートするドキュメントがありません")
        return 0

    success_count = 0

    for doc in documents:
        doc_id: str = doc["id"]
        content: str = doc["content"]
        metadata: dict = doc.get("metadata", {})

        if not content.strip():
            logger.warning("空のドキュメントをスキップします（id=%s）", doc_id)
            continue

        try:
            # テキストを一時ファイルに書き出してGCSなしでアップロード
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".txt",
                delete=False,
                encoding="utf-8",
            ) as f:
                f.write(content)
                tmp_path = f.name

            # RAGファイルとしてコーパスにアップロード
            rag.upload_file(
                corpus_name=corpus_name,
                path=tmp_path,
                display_name=doc_id,
                description=str(metadata),
            )
            success_count += 1
            logger.info("ドキュメントをインポートしました（id=%s）", doc_id)

        except Exception as e:
            logger.error("ドキュメントのインポートに失敗しました（id=%s）: %s", doc_id, e)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    logger.info("インポート完了: %d / %d 件成功", success_count, len(documents))
    return success_count
