from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Server configuration settings."""

    APP_NAME: str = "paper-report-mcp"
    APP_VERSION: str = "0.1.0"
    MAX_RESULTS: int = 50
    BATCH_SIZE: int = 20
    REQUEST_TIMEOUT: int = 60
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    PROXY: str = ""

    @property
    def STORAGE_PATH(self) -> Path:
        """Get the resolved storage path and ensure it exists.

        Returns:
            Path: The absolute storage path.
        """
        path = Path(__file__).parent.parent.parent / "downloads"
        path = path.resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path
