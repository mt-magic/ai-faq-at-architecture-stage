"""
WordPressサイト クローラー
WordPress REST API と sitemap.xml を利用してページ一覧を取得し
本文テキストを抽出してRAG用ドキュメントに変換する
レンタルサーバー負荷軽減のためリクエスト間隔を設ける
"""
import logging
import os
import time

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

WP_SITE_URL = os.environ["WP_SITE_URL"]  # 例: https://example.com
# リクエスト間隔（秒）：レンタルサーバーへの負荷を抑制
CRAWL_INTERVAL_SEC = float(os.environ.get("CRAWL_INTERVAL_SEC", "2.0"))
MAX_PAGES = int(os.environ.get("CRAWL_MAX_PAGES", "200"))


def crawl_wordpress_pages() -> list[dict]:
    """
    WordPressの公開ページを取得してドキュメントリストに変換する
    WordPress REST API（/wp-json/wp/v2/pages, /posts）を優先使用する

    Returns:
        ドキュメントリスト（各要素は {"id": str, "content": str, "metadata": dict}）
    """
    documents: list[dict] = []

    # WordPress REST APIで固定ページを取得
    documents.extend(_fetch_wp_rest_api("pages"))
    # 投稿記事も取得
    documents.extend(_fetch_wp_rest_api("posts"))

    logger.info("WordPressコンテンツを取得しました: %d件", len(documents))
    return documents[:MAX_PAGES]


def _fetch_wp_rest_api(content_type: str) -> list[dict]:
    """
    WordPress REST APIからコンテンツを取得する

    Args:
        content_type: "pages" または "posts"
    """
    documents: list[dict] = []
    page_num = 1

    while True:
        url = f"{WP_SITE_URL}/wp-json/wp/v2/{content_type}"
        try:
            response = httpx.get(
                url,
                params={"per_page": 20, "page": page_num, "status": "publish"},
                timeout=10.0,
                headers={"User-Agent": "AI-FAQ-Bot/1.0"},
            )

            if response.status_code == 400:
                # ページ数を超えた場合は終了
                break
            response.raise_for_status()

            items = response.json()
            if not items:
                break

            for item in items:
                item_id = item.get("id")
                title = item.get("title", {}).get("rendered", "")
                raw_html = item.get("content", {}).get("rendered", "")
                plain_text = _html_to_plain(raw_html)
                link = item.get("link", "")

                if not plain_text.strip():
                    continue

                documents.append({
                    "id": f"wp_{content_type}_{item_id}",
                    "content": f"タイトル: {title}\n\n{plain_text}",
                    "metadata": {
                        "source": "wordpress",
                        "content_type": content_type,
                        "item_id": str(item_id),
                        "url": link,
                    },
                })

            page_num += 1
            time.sleep(CRAWL_INTERVAL_SEC)

        except Exception as e:
            logger.error("WordPress REST APIエラー（type=%s, page=%d）: %s", content_type, page_num, e)
            break

    return documents


def _html_to_plain(html: str) -> str:
    """HTMLタグを除去してプレーンテキストを返す"""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)
