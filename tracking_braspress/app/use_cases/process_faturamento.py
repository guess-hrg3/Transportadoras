from __future__ import annotations
from app.config.settings import Settings
from app.core.logger import get_logger
from app.db.faturamento_repo import FaturamentoRepository
from app.services.braspress_service import BraspressService

class ProcessFaturamento:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        self.repo = FaturamentoRepository(settings)
        self.service = BraspressService(settings)

    def inserir_notas(self) -> None:
        notas = self.repo.get_notas()
        for nf_saida, serie_nf, filial in notas:
            if not self.repo.registro_existe(nf_saida, serie_nf, filial):
                self.repo.insert_faturamento_ocorrencia(nf_saida, serie_nf, filial)
            else:
                self.logger.info(f"Registro já existe: {nf_saida} - {serie_nf} - {filial}")

    def atualizar_notas(self) -> None:
        notas = self.repo.get_notas()
        for nf_saida, serie_nf, filial in notas:
            payload = self.service.fetch_ocorrencia(nf_saida)
            if not payload:
                continue

            self.repo.update_faturamento_ocorrencia(
                nf_saida=nf_saida,
                serie_nf=serie_nf,
                filial=filial,
                cod_ocorrencia=payload["cod_ocorrencia"],
                observacao=payload.get("observacao"),
                data_ocorrencia=payload.get("data_ocorrencia"),
                hora_ocorrencia=payload.get("hora_ocorrencia"),
            )
