from __future__ import annotations
from datetime import datetime
from typing import Optional, Tuple

def parse_braspress_datetime(dt_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Recebe uma string de data/hora e tenta convertê-la para:
    - data: YYYY-MM-DD
    - hora: HH:MM

    Suporta formatos comuns da API (pt-BR) e ISO 8601.
    """
    if not dt_str:
        return None, None

    candidates = [
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]

    for fmt in candidates:
        try:
            dt = datetime.strptime(dt_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")
        except ValueError:
            continue

    # ISO 8601 (com ou sem timezone)
    try:
        iso = dt_str.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")
    except Exception:
        return None, None
