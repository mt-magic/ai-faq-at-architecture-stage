# 本番環境 変数定義
# terraform plan -var-file="environments/prod.tfvars" で使用

project_id = "your-gcp-project-id-prod"
env        = "prod"
region     = "asia-northeast1"

slack_bot_image    = "asia-northeast1-docker.pkg.dev/your-gcp-project-id-prod/ai-faq-repo/slack-bot-service:latest"
customer_api_image = "asia-northeast1-docker.pkg.dev/your-gcp-project-id-prod/ai-faq-repo/customer-api-service:latest"
batch_jobs_image   = "asia-northeast1-docker.pkg.dev/your-gcp-project-id-prod/ai-faq-repo/batch-jobs:latest"

internal_rag_corpus_name = "projects/YOUR_PROJECT_NUMBER/locations/asia-northeast1/ragCorpora/INTERNAL_CORPUS_ID"
customer_rag_corpus_name = "projects/YOUR_PROJECT_NUMBER/locations/asia-northeast1/ragCorpora/CUSTOMER_CORPUS_ID"

redis_tier           = "STANDARD_HA"
redis_memory_size_gb = 2

allowed_origins = ["https://example.com"]
