from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    omie_app_key: str = ""
    omie_app_secret: str = ""
    omie_allow_writes: bool = False
    omie_api_base: str = "https://app.omie.com.br/api/v1"
    omie_service_list_url: str = "https://developer.omie.com.br/service-list/"
    omie_state_dir: Path = Path(".omie_mcp_state")
    omie_http_timeout: float = 45.0

    def require_credentials(self) -> None:
        if not self.omie_app_key or not self.omie_app_secret:
            raise RuntimeError(
                "Credenciais Omie ausentes. Defina OMIE_APP_KEY e OMIE_APP_SECRET em variáveis de ambiente ou .env local."
            )


settings = Settings()
