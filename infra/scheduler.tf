# ===== Cloud Scheduler + Cloud Run Jobs =====

# Slack履歴取り込みバッチ（毎日 02:00 JST）
resource "google_cloud_run_v2_job" "slack_batch" {
  name     = "slack-batch-job"
  location = var.region

  template {
    template {
      service_account = google_service_account.batch_jobs_sa.email

      containers {
        image = var.batch_jobs_image

        env {
          name  = "JOB_TYPE"
          value = "slack_batch"
        }
        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "INTERNAL_RAG_CORPUS_NAME"
          value = var.internal_rag_corpus_name
        }
        env {
          name = "SLACK_BOT_TOKEN"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.slack_bot_token.secret_id
              version = "latest"
            }
          }
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "1Gi"
          }
        }
      }

      max_retries = 2
    }
  }
}

resource "google_cloud_scheduler_job" "slack_batch_trigger" {
  name      = "slack-batch-trigger"
  region    = var.region
  schedule  = "0 2 * * *"   # 毎日 02:00 JST（UTC+9）
  time_zone = "Asia/Tokyo"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.slack_batch.name}:run"

    oauth_token {
      service_account_email = google_service_account.batch_jobs_sa.email
    }
  }

  depends_on = [google_project_service.apis]
}

# Backlog Wiki取り込みバッチ（毎日 03:00 JST）
resource "google_cloud_run_v2_job" "backlog_batch" {
  name     = "backlog-batch-job"
  location = var.region

  template {
    template {
      service_account = google_service_account.batch_jobs_sa.email

      containers {
        image = var.batch_jobs_image

        env {
          name  = "JOB_TYPE"
          value = "backlog_batch"
        }
        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "INTERNAL_RAG_CORPUS_NAME"
          value = var.internal_rag_corpus_name
        }
        env {
          name = "BACKLOG_API_KEY"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.backlog_api_key.secret_id
              version = "latest"
            }
          }
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "1Gi"
          }
        }
      }

      max_retries = 2
    }
  }
}

resource "google_cloud_scheduler_job" "backlog_batch_trigger" {
  name      = "backlog-batch-trigger"
  region    = var.region
  schedule  = "0 3 * * *"   # 毎日 03:00 JST
  time_zone = "Asia/Tokyo"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.backlog_batch.name}:run"

    oauth_token {
      service_account_email = google_service_account.batch_jobs_sa.email
    }
  }
}

# WordPressクロールバッチ（毎週月曜 04:00 JST）
resource "google_cloud_run_v2_job" "webcrawl_batch" {
  name     = "webcrawl-batch-job"
  location = var.region

  template {
    template {
      service_account = google_service_account.batch_jobs_sa.email

      containers {
        image = var.batch_jobs_image

        env {
          name  = "JOB_TYPE"
          value = "webcrawl_batch"
        }
        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "CUSTOMER_RAG_CORPUS_NAME"
          value = var.customer_rag_corpus_name
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "1Gi"
          }
        }
      }

      max_retries = 1
    }
  }
}

resource "google_cloud_scheduler_job" "webcrawl_batch_trigger" {
  name      = "webcrawl-batch-trigger"
  region    = var.region
  schedule  = "0 4 * * 1"   # 毎週月曜 04:00 JST
  time_zone = "Asia/Tokyo"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.webcrawl_batch.name}:run"

    oauth_token {
      service_account_email = google_service_account.batch_jobs_sa.email
    }
  }
}
