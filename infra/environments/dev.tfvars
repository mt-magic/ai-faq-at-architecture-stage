# 開発環境 変数定義
# terraform plan -var-file="environments/dev.tfvars" で使用

project_id = "your-gcp-project-id-dev"
env        = "dev"
region     = "asia-northeast1"

slack_bot_image    = "asia-northeast1-docker.pkg.dev/your-gcp-project-id-dev/ai-faq-repo/slack-bot-service:latest"
customer_api_image = "asia-northeast1-docker.pkg.dev/your-gcp-project-id-dev/ai-faq-repo/customer-api-service:latest"
batch_jobs_image   = "asia-northeast1-docker.pkg.dev/your-gcp-project-id-dev/ai-faq-repo/batch-jobs:latest"

internal_rag_corpus_name = "projects/YOUR_PROJECT_NUMBER/locations/asia-northeast1/ragCorpora/INTERNAL_CORPUS_ID"
customer_rag_corpus_name = "projects/YOUR_PROJECT_NUMBER/locations/asia-northeast1/ragCorpora/CUSTOMER_CORPUS_ID"

redis_tier           = "BASIC"
redis_memory_size_gb = 1

allowed_origins = ["https://dev.example.com"]
