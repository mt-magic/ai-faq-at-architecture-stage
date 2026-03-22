# ===== Cloud Memorystore (Redis) =====
resource "google_redis_instance" "cache" {
  name           = "ai-faq-cache-${var.env}"
  tier           = var.redis_tier
  memory_size_gb = var.redis_memory_size_gb
  region         = var.region

  redis_version = "REDIS_7_0"
  display_name  = "AI FAQ チャンネル権限キャッシュ"

  depends_on = [google_project_service.apis]
}
