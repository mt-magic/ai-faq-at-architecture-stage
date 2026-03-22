variable "project_id" {
  description = "GCPプロジェクトID"
  type        = string
}

variable "region" {
  description = "GCPリージョン"
  type        = string
  default     = "asia-northeast1"
}

variable "env" {
  description = "環境名 (dev / prod)"
  type        = string
}

variable "ar_repo_name" {
  description = "Artifact Registry リポジトリ名"
  type        = string
  default     = "ai-faq-repo"
}

variable "slack_bot_image" {
  description = "Slack Bot Service の Dockerイメージ URI"
  type        = string
}

variable "customer_api_image" {
  description = "Customer API Service の Dockerイメージ URI"
  type        = string
}

variable "batch_jobs_image" {
  description = "Batch Jobs の Dockerイメージ URI"
  type        = string
}

variable "internal_rag_corpus_name" {
  description = "社内コーパスのRAGリソース名"
  type        = string
}

variable "customer_rag_corpus_name" {
  description = "顧客コーパスのRAGリソース名"
  type        = string
}

variable "redis_tier" {
  description = "Cloud Memorystore Redis のサービスティア"
  type        = string
  default     = "BASIC"
}

variable "redis_memory_size_gb" {
  description = "Cloud Memorystore Redis のメモリサイズ (GB)"
  type        = number
  default     = 1
}

variable "allowed_origins" {
  description = "CORSを許可するWordPressサイトのオリジン"
  type        = list(string)
}
