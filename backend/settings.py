from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), extra="ignore")

    config_dir: Path = ROOT / "config"
    data_dir: Path = ROOT / "data"
    fred_api_key: str = ""
    newsdata_api_key: str = ""
    enable_hf_classifier: bool = False

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "deepseek-r1:latest"
    ollama_timeout_seconds: float = 300.0
    chat_enrichment_timeout_seconds: float = 12.0
    chat_live_enrichment_enabled: bool = True

    @property
    def db_path(self) -> Path:
        return self.data_dir / "analytics.duckdb"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    @property
    def snapshots_dir(self) -> Path:
        return self.data_dir / "snapshots"


settings = Settings()
