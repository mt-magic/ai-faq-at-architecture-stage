"""
Backlog Wiki フェッチャー
Backlog REST API でWiki記事一覧を取得し、MarkdownをテキストにしてRAG用ドキュメントに変換する
"""
import logging
import os

import httpx
import markdown

logger = logging.getLogger(__name__)

BACKLOG_API_KEY = os.environ["BACKLOG_API_KEY"]
BACKLOG_SPACE = os.environ["BACKLOG_SPACE"]       #例: yourcompany
BACKLOG_PROJECT_ID = os.environ["BACKLOG_PROJECT_ID"]

BACKLOG_BASE_URL = f"https://{BACKLOG_SPACE}.backlog.com/api/v2"


def fetch_all_wikis() -> list[dict]:
    """
    BacklogのWiki記事を全件取得してドキュメントリストに変換する

    Returns:
        ドキュメントリスト（各要素は {"id": str, "content": str, "metadata": dict}）
    """
    wiki_list = _get_wiki_list()
    documents: list[dict] = []

    for wiki in wiki_list:
        wiki_id = wiki["id"]
        detail = _get_wiki_detail(wiki_id)
        if not detail:
            continue

        # MarkdownをプレーンテキストにしてRAGに最適化
        raw_content = detail.get("content", "")
        plain_text = _markdown_to_plain(raw_content)

        if not plain_text.strip():
            continue

        documents.append({
            "id": f"backlog_wiki_{wiki_id}",
            "content": f"タイトル: {detail['name']}\n\n{plain_text}",
            "metadata": {
                "source": "backlog",
                "wiki_id": str(wiki_id),
                "wiki_name": detail["name"],
                "project_id": BACKLOG_PROJECT_ID,
            },
        })

    logger.info("Backlog Wikiを取得しました: %d件", len(documents))
    return documents


def _get_wiki_list() -> list[dict]:
    """Wiki記事の一覧を取得する"""
    try:
        response = httpx.get(
            f"{BACKLOG_BASE_URL}/wikis",
            params={"apiKey": BACKLOG_API_KEY, "projectIdOrKey": BACKLOG_PROJECT_ID},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("Backlog Wiki一覧の取得に失敗しました: %s", e)
        return []


def _get_wiki_detail(wiki_id: int) -> dict | None:
    """Wiki記事の詳細（本文）を取得する"""
    try:
        response = httpx.get(
            f"{BACKLOG_BASE_URL}/wikis/{wiki_id}",
            params={"apiKey": BACKLOG_API_KEY},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("Backlog Wiki詳細の取得に失敗しました（id=%s）: %s", wiki_id, e)
        return None


def _markdown_to_plain(md_text: str) -> str:
    """MarkdownをHTMLに変換してからタグを除去してプレーンテキストにする"""
    html = markdown.markdown(md_text)
    # 簡易タグ除去
    import re
    return re.sub(r"<[^>]+>", "", html).strip()
