import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    # API Braspress
    API_CNPJ: str = os.getenv("API_CNPJ", "").strip()
    API_USER: str = os.getenv("API_USER", "").strip()
    API_PASSWORD: str = os.getenv("API_PASSWORD", "").strip()
    API_URL: str = os.getenv("API_URL", "").strip()

    # Banco
    DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server").strip()
    DB_SERVER: str = os.getenv("DB_SERVER", "").strip()
    DB_DATABASE: str = os.getenv("DB_DATABASE", "").strip()
    DB_USER: str = os.getenv("DB_USER", "").strip()
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "").strip()

    # Outros
    FATURAMENTO_START_DATE: str = os.getenv("FATURAMENTO_START_DATE", "20251001").strip()
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    REQUEST_RETRIES: int = int(os.getenv("REQUEST_RETRIES", "3"))
    REQUEST_BACKOFF: float = float(os.getenv("REQUEST_BACKOFF", "0.5"))
    LOG_DIR: str = os.getenv("LOG_DIR", "logs").strip()

    def driver_with_braces(self) -> str:
        d = (self.DB_DRIVER or "").strip().strip("{}")
        return "{" + d + "}"

