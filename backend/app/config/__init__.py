from pydantic_settings import BaseSettings, SettingsConfigDict
from .categories import (
    CATEGORY_TAXONOMY,
    CATEGORY_DISPLAY_LABELS,
    SUBCATEGORY_TO_TOP_LEVEL,
    normalize_category_name,
    get_subcategories_for_category,
    is_valid_category,
)

class Settings(BaseSettings):
    ENVIRONMENT: str = 'development'
    JWT_SECRET: str | None = None
    SECRET_KEY: str = 'vignex-super-secret-production-key-for-auth-2026'
    DATABASE_URL: str = 'sqlite:///./vignex.db'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = 'http://localhost:5173'
    ALGORITHM: str = 'HS256'
    PORT: int = 8000
    LOG_LEVEL: str = 'INFO'
    UPLOAD_DIRECTORY: str = 'uploads'
    ENABLE_DEMO_SEEDING: bool = False

    # AI Configuration (Backend-only, never exposed to client)
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = 'gemini-3.6-flash'
    AI_PROVIDER: str = 'gemini'

    @property
    def jwt_secret_key(self) -> str:
        return self.JWT_SECRET or self.SECRET_KEY

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == 'production'

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]

    def validate_production_readiness(self) -> None:
        """Validate critical configuration constraints for production safety."""
        if not self.is_production:
            return

        default_keys = {
            'vignex-super-secret-production-key-for-auth-2026',
            'change-me-to-a-random-secret-key',
            'secret',
            'password123',
        }
        active_key = self.jwt_secret_key
        if not active_key or active_key in default_keys or len(active_key) < 24:
            raise ValueError(
                "CRITICAL SECURITY ERROR: Production deployment requires a secure, high-entropy JWT_SECRET or SECRET_KEY."
            )

        if '*' in self.cors_origin_list and len(self.cors_origin_list) == 1:
            raise ValueError(
                "CRITICAL SECURITY ERROR: Wildcard CORS ('*') is not permitted in production with credentials enabled."
            )

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
