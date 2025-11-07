from __future__ import annotations
import base64
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any, Tuple

from app.config.settings import Settings
from app.core.logger import get_logger
from app.core.constants import STATUS_MAP
from app.core.utils import parse_braspress_datetime

class BraspressService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        s = requests.Session()
        retries = Retry(
            total=self.settings.REQUEST_RETRIES,
            backoff_factor=self.settings.REQUEST_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        return s

    def _auth_header(self) -> Dict[str, str]:
        credenciais = f"{self.settings.API_USER}:{self.settings.API_PASSWORD}"
        auth_encoded = base64.b64encode(credenciais.encode()).decode()
        return {
            "Authorization": f"Basic {auth_encoded}",
            "Content-Type": "application/json",
            "User-Agent": "GuessBrasilTracking/1.0",
        }

    def _build_url(self, nf_saida: str) -> str:
        nf_api = (nf_saida or "").lstrip('0')
        return f"{self.settings.API_URL}/{self.settings.API_CNPJ}/{nf_api}/json"

    def fetch_ocorrencia(self, nf_saida: str) -> Optional[Dict[str, Any]]:
        """Consulta a API e mapeia os campos necessários para atualização."""
        url = self._build_url(nf_saida)
        try:
            resp = self.session.get(url, headers=self._auth_header(), timeout=self.settings.REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ReadTimeout:
            self.logger.warning(f"Timeout ao consultar API Braspress para NF {nf_saida}")
            return None
        except requests.RequestException as e:
            self.logger.error(f"Erro na requisição Braspress para NF {nf_saida}: {e}", exc_info=True)
            return None
        except ValueError:
            self.logger.error(f"Resposta inválida (JSON) para NF {nf_saida}", exc_info=True)
            return None

        conhecimentos = data.get("conhecimentos", [])
        if not conhecimentos:
            self.logger.warning(f"Nenhum conhecimento encontrado para NF {nf_saida}")
            return None

        conhecimento = conhecimentos[0] or {}
        timeline = conhecimento.get("timeLine", []) or []
        ultima_oc = timeline[-1] if timeline else {}

        status_api = (conhecimento.get("status") or "").strip().upper()
        cod_ocorrencia = STATUS_MAP.get(status_api, "00")

        observacao = ultima_oc.get("descricao") or conhecimento.get("ultimaOcorrencia")
        dt_full = ultima_oc.get("data") or conhecimento.get("dataOcorrencia")
        data_ocorrencia, hora_ocorrencia = parse_braspress_datetime(dt_full)

        return {
            "cod_ocorrencia": cod_ocorrencia,
            "observacao": observacao,
            "data_ocorrencia": data_ocorrencia,
            "hora_ocorrencia": hora_ocorrencia,
            "status_api": status_api,
        }
