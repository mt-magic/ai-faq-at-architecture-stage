# ===== サービスアカウント =====
resource "google_service_account" "slack_bot_sa" {
  account_id   = "slack-bot-sa"
  display_name = "Slack Bot Service Account"
}

resource "google_service_account" "customer_api_sa" {
  account_id   = "customer-api-sa"
  display_name = "Customer API Service Account"
}

resource "google_service_account" "batch_jobs_sa" {
  account_id   = "batch-jobs-sa"
  display_name = "Batch Jobs Service Account"
}

# ===== Cloud Run: Slack Bot Service =====
resource "google_cloud_run_v2_service" "slack_bot" {
  name     = "slack-bot-service"
  location = var.region

  template {
    service_account = google_service_account.slack_bot_sa.email

    containers {
      image = var.slack_bot_image

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_LOCATION"
        value = var.region
      }
      env {
        name  = "INTERNAL_RAG_CORPUS_NAME"
        value = var.internal_rag_corpus_name
      }
      env {
        name  = "REDIS_HOST"
        value = google_redis_instance.cache.host
      }

      # Secret Manager から機密情報を注入
      env {
        name = "SLACK_BOT_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.slack_bot_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "SLACK_SIGNING_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.slack_signing_secret.secret_id
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  depends_on = [google_project_service.apis]
}

# ===== Cloud Run: Customer API Service =====
resource "google_cloud_run_v2_service" "customer_api" {
  name     = "customer-api-service"
  location = var.region

  template {
    service_account = google_service_account.customer_api_sa.email

    containers {
      image = var.customer_api_image

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_LOCATION"
        value = var.region
      }
      env {
        name  = "CUSTOMER_RAG_CORPUS_NAME"
        value = var.customer_rag_corpus_name
      }
      env {
        name  = "ALLOWED_ORIGINS"
        value = join(",", var.allowed_origins)
      }
      env {
        name = "RECAPTCHA_SITE_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.recaptcha_site_key.secret_id
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 20
    }
  }

  depends_on = [google_project_service.apis]
}

# 顧客APIは公開エンドポイント（reCAPTCHAで保護）
resource "google_cloud_run_v2_service_iam_member" "customer_api_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.customer_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ===== Secret Manager =====
resource "google_secret_manager_secret" "slack_bot_token" {
  secret_id = "slack-bot-token"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "slack_signing_secret" {
  secret_id = "slack-signing-secret"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "recaptcha_site_key" {
  secret_id = "recaptcha-site-key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "backlog_api_key" {
  secret_id = "backlog-api-key"
  replication {
    auto {}
  }
}
