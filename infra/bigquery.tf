# ===== BigQuery 利用ログ =====
resource "google_bigquery_dataset" "ai_faq_logs" {
  dataset_id    = "ai_faq_logs"
  friendly_name = "AI FAQ 利用ログ"
  description   = "従業員・顧客向けFAQサービスの利用ログ"
  location      = "asia-northeast1"

  # ログの保持期間：365日
  default_table_expiration_ms = 365 * 24 * 60 * 60 * 1000

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_table" "usage_logs" {
  dataset_id = google_bigquery_dataset.ai_faq_logs.dataset_id
  table_id   = "usage_logs"
  description = "FAQ利用ログテーブル"

  schema = jsonencode([
    { name = "timestamp",   type = "TIMESTAMP", mode = "REQUIRED", description = "リクエスト日時" },
    { name = "service",     type = "STRING",    mode = "REQUIRED", description = "サービス種別 (slack-bot / customer-api)" },
    { name = "user_id",     type = "STRING",    mode = "NULLABLE", description = "SlackユーザーID（従業員向けのみ）" },
    { name = "user_email",  type = "STRING",    mode = "NULLABLE", description = "ユーザーメールアドレス（従業員向けのみ）" },
    { name = "channel_id",  type = "STRING",    mode = "NULLABLE", description = "SlackチャンネルID（従業員向けのみ）" },
    { name = "session_id",  type = "STRING",    mode = "NULLABLE", description = "セッションID（顧客向けのみ）" },
    { name = "question",    type = "STRING",    mode = "REQUIRED", description = "ユーザーの質問テキスト" },
    { name = "answer",      type = "STRING",    mode = "REQUIRED", description = "生成された回答テキスト" },
    { name = "success",     type = "BOOLEAN",   mode = "REQUIRED", description = "RAG処理の成功フラグ" },
    { name = "latency_ms",  type = "INTEGER",   mode = "REQUIRED", description = "処理時間（ミリ秒）" },
  ])

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }
}
