"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_env: str = "dev"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Database
    database_url: str = "sqlite:///./app.db"

    # Datadog
    dd_mode: str = "mock"  # mock or live
    datadog_site: Optional[str] = None
    datadog_api_key: Optional[str] = None
    datadog_app_key: Optional[str] = None

    # Minimax
    minimax_api_key: str = ""
    minimax_model: str = "abab5.5-chat"
    minimax_temperature: float = 0.3

    # TestSprite
    testsprite_api_key: Optional[str] = None
    testsprite_mode: str = "mock"  # mock or live

    # AWS Bedrock AgentCore
    aws_region: Optional[str] = None
    agentcore_memory_id: Optional[str] = None
    agentcore_gateway_id: Optional[str] = None

    # Slack (optional)
    slack_webhook_url: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
