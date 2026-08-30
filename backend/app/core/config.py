from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CX Reply Assistant"
    environment: str = "development"
    api_prefix: str = "/api"

    database_url: str

    supabase_jwt_secret: str

    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection: str = "cx_knowledge"

    openrouter_api_key: str
    openrouter_model: str

    # embedding_model: str = (
    #     "sentence-transformers/all-MiniLM-L6-v2"
    # )

    rag_top_k: int = 3
    rag_relevance_threshold: float = 0.55

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()