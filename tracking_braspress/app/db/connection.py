from __future__ import annotations
import pyodbc
from app.config.settings import Settings

def _ensure_braces(driver: str) -> str:
    d = (driver or "").strip().strip("{}")
    return "{" + d + "}"

def get_db_connection(settings: Settings):
    conn_str = (
        f"DRIVER={_ensure_braces(settings.DB_DRIVER)};"
        f"SERVER={settings.DB_SERVER};"
        f"DATABASE={settings.DB_DATABASE};"
        f"UID={settings.DB_USER};"
        f"PWD={settings.DB_PASSWORD}"
    )
    return pyodbc.connect(conn_str)
