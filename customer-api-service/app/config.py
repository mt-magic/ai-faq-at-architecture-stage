from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # GCPプロジェクト設定
    gcp_project_id: str
    gcp_location: str = "asia-northeast1"

    # Vertex AI RAG Engine（顧客コーパス）
    rag_corpus_name: str  # projects/{id}/locations/{loc}/ragCorpora/{corpus_id}

    # Gemini モデル
    gemini_model: str = "gemini-2.0-flash-001"

    # reCAPTCHA Enterprise
    recaptcha_site_key: str
    recaptcha_project_id: str

    # BigQuery
    bigquery_dataset: str = "ai_faq_logs"
    bigquery_table: str = "usage_logs"

    # RAG設定
    rag_top_k: int = 5
    rag_distance_threshold: float = 0.3

    # CORS許可オリジン（WordPressサイトのドメイン）
    allowed_origins: list[str] = ["https://example.com"]

    class Config:
        env_file = ".env"


settings = Settings()
