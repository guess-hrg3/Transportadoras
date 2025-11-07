from __future__ import annotations
from typing import List, Tuple, Optional
from app.config.settings import Settings
from app.core.logger import get_logger
from app.db.connection import get_db_connection
from app.core.utils import parse_braspress_datetime

class FaturamentoRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)

    def get_notas(self) -> List[Tuple[str, str, str]]:
        """Busca notas a partir da data configurada que atendem aos critérios."""
        sql = """
            SELECT NF_SAIDA, SERIE_NF, FILIAL
            FROM FATURAMENTO
            WHERE TRANSPORTADORA='BRASPRESS'
              AND EMISSAO >= ?
              AND PROTOCOLO_AUTORIZACAO_NFE IS NOT NULL
        """
        try:
            with get_db_connection(self.settings) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, self.settings.FATURAMENTO_START_DATE)
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    nf = str(row[0]).strip() if row[0] is not None else ""
                    serie = str(row[1]).strip() if row[1] is not None else ""
                    filial = str(row[2]).strip() if row[2] is not None else ""
                    result.append((nf, serie, filial))
                return result
        except Exception as e:
            self.logger.error(f"Erro ao buscar notas: {e}", exc_info=True)
            return []

    def registro_existe(self, nf_saida: str, serie_nf: str, filial: str) -> bool:
        sql = """
            SELECT 1
            FROM FATURAMENTO_OCORRENCIAS
            WHERE NF_SAIDA=? AND SERIE_NF=? AND FILIAL=?
        """
        try:
            with get_db_connection(self.settings) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, nf_saida, serie_nf, filial)
                return cursor.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Erro ao verificar registro existente ({nf_saida}-{serie_nf}-{filial}): {e}", exc_info=True)
            return False

    def _gerar_id_ocorrencia(self, cursor) -> Optional[str]:
        try:
            cursor.execute("""
                DECLARE @SEQ VARCHAR(20);
                EXEC LX_SEQUENCIAL @TABELA_COLUNA='FATURAMENTO_OCORRENCIAS.ID_OCORRENCIA', @SEQUENCIA=@SEQ OUTPUT;
                SELECT @SEQ AS SEQ;
            """)
            row = cursor.fetchone()
            return str(row[0]) if row and row[0] is not None else None
        except Exception as e:
            self.logger.error(f"Erro ao gerar ID_OCORRENCIA: {e}", exc_info=True)
            return None

    def insert_faturamento_ocorrencia(self, nf_saida: str, serie_nf: str, filial: str, data_ocorrencia_full: Optional[str] = None) -> None:
        try:
            with get_db_connection(self.settings) as conn:
                cursor = conn.cursor()
                id_ocorrencia = self._gerar_id_ocorrencia(cursor)
                if not id_ocorrencia:
                    self.logger.error("Não foi possível gerar ID_OCORRENCIA; inserção abortada.")
                    return

                data_ocorrencia, hora_ocorrencia = parse_braspress_datetime(data_ocorrencia_full)

                cursor.execute("""
                    INSERT INTO FATURAMENTO_OCORRENCIAS (
                        ID_OCORRENCIA, NF_SAIDA, SERIE_NF, FILIAL,
                        COD_OCORRENCIA, OBSERVACAO,
                        DATA_OCORRENCIA, HORA_OCORRENCIA
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, id_ocorrencia, nf_saida, serie_nf, filial, "00", None,
                     data_ocorrencia, hora_ocorrencia)

                conn.commit()
                self.logger.info(
                    f"Registro inserido: {nf_saida} - {serie_nf} - {filial} "
                    f"(COD_OCORRENCIA='00', ID_OCORRENCIA={id_ocorrencia}, "
                    f"DATA_OCORRENCIA={data_ocorrencia}, HORA_OCORRENCIA={hora_ocorrencia})"
                )
        except Exception as e:
            self.logger.error(f"Erro ao inserir ocorrência: {nf_saida}-{serie_nf}-{filial}: {e}", exc_info=True)

    def update_faturamento_ocorrencia(self, nf_saida: str, serie_nf: str, filial: str,
                                      cod_ocorrencia: str, observacao: Optional[str],
                                      data_ocorrencia: Optional[str], hora_ocorrencia: Optional[str]) -> None:
        sql = """
            UPDATE FATURAMENTO_OCORRENCIAS
               SET COD_OCORRENCIA=?,
                   OBSERVACAO=?,
                   DATA_OCORRENCIA=ISNULL(DATA_OCORRENCIA, ?),
                   HORA_OCORRENCIA=ISNULL(HORA_OCORRENCIA, ?)
             WHERE NF_SAIDA=? AND SERIE_NF=? AND FILIAL=?
               AND (COD_OCORRENCIA IS NULL OR COD_OCORRENCIA != '01')
        """
        try:
            with get_db_connection(self.settings) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, cod_ocorrencia, observacao, data_ocorrencia, hora_ocorrencia,
                               nf_saida, serie_nf, filial)
                conn.commit()
                self.logger.info(
                    f"NF {nf_saida} atualizada: COD_OCORRENCIA={cod_ocorrencia}, "
                    f"OBSERVACAO={observacao}, DATA_OCORRENCIA={data_ocorrencia}, HORA_OCORRENCIA={hora_ocorrencia}"
                )
        except Exception as e:
            self.logger.error(f"Erro ao atualizar NF {nf_saida}: {e}", exc_info=True)
