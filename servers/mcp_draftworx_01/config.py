"""
Configuration management for Draftworx MCP server.
Loads environment variables and provides typed access.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class DraftworxConfig(BaseSettings):
    """Configuration for Draftworx MCP Server"""

    # Draftworx OAuth Configuration
    auth_server_url: str = os.getenv("AUTH_SERVER_URL", "https://login.cloud.draftworx.com")
    client_id: str = os.getenv("CLIENT_ID", "")
    client_secret: str = os.getenv("CLIENT_SECRET", "")
    client_scope: str = os.getenv("CLIENT_SCOPE", "openid profile email api")

    # Draftworx API Configuration
    api_server_url: str = os.getenv("API_SERVER_URL", "https://api.cloud.draftworx.com")
    draftworx_practice_id: str = os.getenv("DRAFTWORX_PRACTICE_ID", "")
    draftworx_client_id: str = os.getenv("DRAFTWORX_CLIENT_ID", "")
    draftworx_financialyear_id: str = os.getenv("DRAFTWORX_FINANCIALYEAR_ID", "")

    # Security
    cookie_encryption_key: str = os.getenv("COOKIE_ENCRYPTION_KEY", "")

    # Server Configuration
    server_port: int = int(os.getenv("PORT", "8000"))
    server_host: str = os.getenv("HOST", "0.0.0.0")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global config instance
config = DraftworxConfig()


def get_config() -> DraftworxConfig:
    """Get the global configuration instance"""
    return config


def validate_config() -> None:
    """Validate that required configuration is present"""
    required_fields = [
        ("api_server_url", "API_SERVER_URL"),
        ("draftworx_practice_id", "DRAFTWORX_PRACTICE_ID"),
        ("draftworx_client_id", "DRAFTWORX_CLIENT_ID"),
        ("draftworx_financialyear_id", "DRAFTWORX_FINANCIALYEAR_ID"),
    ]

    missing = []
    for field, env_var in required_fields:
        value = getattr(config, field)
        if not value:
            missing.append(env_var)

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Please set these in your .env file or environment."
        )
