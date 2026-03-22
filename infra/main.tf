terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Terraform stateはGCS バケットで管理する
  backend "gcs" {
    # terraform init -backend-config="bucket=YOUR_BUCKET" で指定
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ===== 有効化するAPI =====
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "aiplatform.googleapis.com",
    "bigquery.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudscheduler.googleapis.com",
    "recaptchaenterprise.googleapis.com",
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# ===== Artifact Registry =====
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = var.ar_repo_name
  format        = "DOCKER"
  description   = "AI FAQ サービス Dockerイメージリポジトリ"

  depends_on = [google_project_service.apis]
}
