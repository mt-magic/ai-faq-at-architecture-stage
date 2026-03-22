output "slack_bot_service_url" {
  description = "Slack Bot Service の Cloud Run URL"
  value       = google_cloud_run_v2_service.slack_bot.uri
}

output "customer_api_service_url" {
  description = "Customer API Service の Cloud Run URL"
  value       = google_cloud_run_v2_service.customer_api.uri
}

output "redis_host" {
  description = "Cloud Memorystore Redis のホスト"
  value       = google_redis_instance.cache.host
}

output "bigquery_table" {
  description = "BigQuery 利用ログテーブルID"
  value       = "${var.project_id}.${google_bigquery_dataset.ai_faq_logs.dataset_id}.${google_bigquery_table.usage_logs.table_id}"
}
