"""
Cloud Run Jobs エントリポイント
JOB_TYPE 環境変数で実行するバッチを切り替える
  slack_batch   → Slack履歴取り込み
  backlog_batch → Backlog Wiki取り込み
  webcrawl_batch → WordPressクロール取り込み
"""
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    job_type = os.environ.get("JOB_TYPE", "")

    if job_type == "slack_batch":
        from slack_batch.main import run
        run()
    elif job_type == "backlog_batch":
        from backlog_batch.main import run
        run()
    elif job_type == "webcrawl_batch":
        from webcrawl_batch.main import run
        run()
    else:
        logger.error("不明なJOB_TYPE: '%s'. slack_batch / backlog_batch / webcrawl_batch のいずれかを指定してください。", job_type)
        sys.exit(1)


if __name__ == "__main__":
    main()
