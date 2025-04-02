from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Summit SEO API"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database Configuration
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str | None = None
    SQLALCHEMY_DATABASE_URI: str | None = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, any]) -> any:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Admin User Configuration
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str = ""  # For admin operations bypassing RLS
    
    # LiteLLM Configuration
    LITELLM_DEFAULT_MODEL: str = "gpt-3.5-turbo"
    LITELLM_DEFAULT_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    LITELLM_FALLBACK_MODELS: str = ""  # Comma-separated list of fallback models
    LITELLM_ENABLE_COST_TRACKING: bool = False
    LITELLM_MAX_BUDGET: float = 0.0
    LITELLM_ENABLE_CACHING: bool = False
    LITELLM_CACHE_TYPE: str = "redis"
    LITELLM_CACHE_HOST: str = ""
    LITELLM_CACHE_PORT: int = 6379
    LITELLM_CACHE_PASSWORD: str = ""
    LITELLM_VERBOSE: bool = False
    LITELLM_MODEL_CONFIG_PATH: str = ""
    
    # LLM Provider API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    AZURE_API_KEY: str = ""
    COHERE_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODELS: str = ""  # Comma-separated list of available Ollama models
    OLLAMA_ENABLE: bool = False
    
    # OpenRouter Configuration
    OPENROUTER_ENABLE: bool = False
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_TIMEOUT: int = 60

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 