from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ASSISTANT_")

    llm_provider: Literal["ollama", "openai", "anthropic"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    data_dir: Path = Path("data")

    @property
    def db_path(self) -> Path:
        return self.data_dir / "assistant.db"

    # Paths for Oauth to gmail
    secrets_dir: Path = Path("secrets")

    @property
    def credentials_path(self) -> Path:
        return self.secrets_dir / "credentials.json"

    @property
    def token_path(self) -> Path:
        return self.secrets_dir / "token.json"
