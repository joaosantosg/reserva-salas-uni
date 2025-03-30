from typing import List, Optional
from app.services.base_service import BaseService
from app.repository.auditoria_repository import AuditoriaRepository
from app.model.auditoria_model import AuditoriaReserva
from app.util.datetime_utils import DateTimeUtils
from app.util.json_utils import serialize_to_json


class AuditoriaService(BaseService):
    def __init__(self, auditoria_repository: AuditoriaRepository):
        self.auditoria_repository = auditoria_repository

    def registrar_auditoria(
        self,
        reserva_id: Optional[str] = None,
        reserva_recorrente_id: Optional[str] = None,
        acao: str = None,
        dados_anteriores: dict = None,
        dados_novos: dict = None,
        usuario_id: str = None,
        ip_address: str = None,
        motivo: str = None,
    ) -> AuditoriaReserva:
        """
        Registra uma nova auditoria no sistema.
        """
        # Serializa os dados para JSON usando o encoder customizado
        dados_anteriores_json = (
            serialize_to_json(dados_anteriores) if dados_anteriores else None
        )
        dados_novos_json = serialize_to_json(dados_novos) if dados_novos else None

        return self.auditoria_repository.criar(
            reserva_id=reserva_id,
            reserva_recorrente_id=reserva_recorrente_id,
            acao=acao,
            dados_anteriores=dados_anteriores_json,
            dados_novos=dados_novos_json,
            usuario_id=usuario_id,
            ip_address=ip_address,
            motivo=motivo,
        )

    def obter_historico_reserva(self, reserva_id: str) -> List[AuditoriaReserva]:
        """
        Obtém o histórico completo de auditorias de uma reserva.
        """
        return self.auditoria_repository.listar_por_reserva(reserva_id)

    def obter_historico_reserva_recorrente(
        self, reserva_recorrente_id: str
    ) -> List[AuditoriaReserva]:
        """
        Obtém o histórico completo de auditorias de uma reserva recorrente.
        """
        return self.auditoria_repository.listar_por_reserva_recorrente(
            reserva_recorrente_id
        )

    def obter_historico_usuario(self, usuario_id: str) -> List[AuditoriaReserva]:
        """
        Obtém o histórico completo de auditorias realizadas por um usuário.
        """
        return self.auditoria_repository.listar_por_usuario(usuario_id)

    def obter_historico_periodo(
        self, data_inicio: DateTimeUtils, data_fim: DateTimeUtils
    ) -> List[AuditoriaReserva]:
        """
        Obtém o histórico de auditorias em um período específico.
        """
        return self.auditoria_repository.listar_por_periodo(data_inicio, data_fim)

    def registrar_criacao_reserva(
        self,
        reserva_id: str,
        dados_novos: dict,
        usuario_id: str,
        ip_address: str,
    ) -> AuditoriaReserva:
        """
        Registra a criação de uma nova reserva.
        """
        return self.registrar_auditoria(
            reserva_id=reserva_id,
            acao="criar",
            dados_novos=dados_novos,
            usuario_id=usuario_id,
            ip_address=ip_address,
        )

    def registrar_atualizacao_reserva(
        self,
        reserva_id: str,
        dados_anteriores: dict,
        dados_novos: dict,
        usuario_id: str,
        ip_address: str,
        motivo: Optional[str] = None,
    ) -> AuditoriaReserva:
        """
        Registra a atualização de uma reserva existente.
        """
        return self.registrar_auditoria(
            reserva_id=reserva_id,
            acao="atualizar",
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
            usuario_id=usuario_id,
            ip_address=ip_address,
            motivo=motivo,
        )

    def registrar_cancelamento_reserva(
        self,
        reserva_id: str,
        dados_anteriores: dict,
        usuario_id: str,
        ip_address: str,
        motivo: str,
    ) -> AuditoriaReserva:
        """
        Registra o cancelamento de uma reserva.
        """
        return self.registrar_auditoria(
            reserva_id=reserva_id,
            acao="cancelar",
            dados_anteriores=dados_anteriores,
            usuario_id=usuario_id,
            ip_address=ip_address,
            motivo=motivo,
        )
