from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # GCPプロジェクト設定
    gcp_project_id: str
    gcp_location: str = "asia-northeast1"

    # Vertex AI RAG Engine（社内コーパス）
    rag_corpus_name: str  # projects/{id}/locations/{loc}/ragCorpora/{corpus_id}

    # Gemini モデル
    gemini_model: str = "gemini-2.0-flash-001"

    # Slack設定（Secret Managerから取得）
    slack_bot_token: str
    slack_signing_secret: str

    # Cloud Memorystore (Redis)
    redis_host: str
    redis_port: int = 6379
    redis_ttl_seconds: int = 600  # 10分

    # BigQuery
    bigquery_dataset: str = "ai_faq_logs"
    bigquery_table: str = "usage_logs"

    # RAG設定
    rag_top_k: int = 5
    rag_distance_threshold: float = 0.3

    class Config:
        env_file = ".env"


# シングルトンとして使用
settings = Settings()
