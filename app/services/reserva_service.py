from uuid import UUID
from datetime import datetime
from typing import List

from app.repository.reserva_repository import ReservaRepository
from app.repository.sala_repository import SalaRepository
from app.repository.usuario_repository import UsuarioRepository
from app.core.commons.exceptions import NotFoundException, BusinessException
from app.util.datetime_utils import DateTimeUtils
from app.model.reserva_model import Reserva
from app.model.reserva_recorrente_model import ReservaRecorrente
from app.schema.reserva_schema import (
    ReservaCreate,
    ReservaUpdate,
    ReservaFiltros,
    ReservasPaginadas,
)

from app.services.email_service import EmailService
from app.services.auditoria_service import AuditoriaService


class ReservaService:
    """Serviço responsável pela gestão de reservas regulares"""

    def __init__(
        self,
        reserva_repository: ReservaRepository,
        sala_repository: SalaRepository,
        usuario_repository: UsuarioRepository,
        email_service: EmailService,
        auditoria_service: AuditoriaService,
    ):
        self.reserva_repository = reserva_repository
        self.sala_repository = sala_repository
        self.usuario_repository = usuario_repository
        self.email_service = email_service
        self.auditoria_service = auditoria_service

    def get_by_id(self, reserva_id: UUID) -> Reserva:
        """Busca uma reserva pelo ID"""
        reserva = self.reserva_repository.get_by_id(reserva_id)
        if not reserva:
            raise NotFoundException(f"Reserva com ID {reserva_id} não encontrada")
        return reserva

    def create(self, reserva_data: ReservaCreate, usuario_id: UUID, curso_usuario: str) -> Reserva:
        """Cria uma nova reserva"""
        # Busca a sala
        sala = self.sala_repository.get_by_id(reserva_data.sala_id)
        if not sala:
            raise NotFoundException(
                f"Sala com ID {reserva_data.sala_id} não encontrada"
            )
        print(f"Sala com ID {reserva_data.sala_id} é restrita para o curso {sala.curso_restrito}")
        print(f"Curso do usuário: {curso_usuario}")
        if sala.uso_restrito and curso_usuario != sala.curso_restrito:
            print(f"Sala com ID {reserva_data.sala_id} é restrita para o curso {sala.curso_restrito}")
            raise BusinessException(
                f"Sala {sala.identificacao_sala} é restrita para o curso {sala.curso_restrito}"
            )
        # Busca o usuário
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundException(f"Usuário com ID {usuario_id} não encontrado")

        # Valida datas e horários
        self._validar_datas(reserva_data.inicio, reserva_data.fim)
        
        # Verifica conflitos antes de criar
        self._verificar_conflitos(reserva_data, reserva_id=None)



        # Cria a reserva
        reserva = Reserva(**reserva_data.model_dump())
        reserva.usuario_id = usuario_id
        reserva = self.reserva_repository.save(reserva)

        # Registra a auditoria
        # self.auditoria_service.registrar_criacao_reserva(
        #     reserva_id=reserva.id,
        #     dados_novos=reserva.__dict__,
        #     usuario_id=usuario_id,
        #     ip_address="",
        # )

        # Envia notificações
        self.email_service.notificar_reserva_criada(reserva, usuario)

        return reserva

    def update(
        self, reserva_id: UUID, reserva_data: ReservaUpdate, usuario_id: UUID
    ) -> Reserva:
        """Atualiza uma reserva existente"""
        # Busca a reserva
        reserva = self.reserva_repository.get_by_id(reserva_id)
        if not reserva:
            raise NotFoundException(f"Reserva com ID {reserva_id} não encontrada")

        # Verifica se o usuário é o dono da reserva
        if reserva.usuario_id != usuario_id:
            raise BusinessException(
                "Você não tem permissão para atualizar esta reserva"
            )

        # Valida datas e horários se foram alterados
        if reserva_data.inicio or reserva_data.fim:
            inicio = reserva_data.inicio or reserva.inicio
            fim = reserva_data.fim or reserva.fim
            self._validar_datas(inicio, fim)

            # Verifica conflitos com a nova data/hora
            self._verificar_conflitos(reserva_data, reserva_id)

        # Atualiza a reserva
        reserva = self.reserva_repository.save(reserva)

        # Registra a auditoria
        # self.auditoria_service.registrar_atualizacao_reserva(
        #     reserva_id=reserva_id,
        #     dados_anteriores=reserva.__dict__,
        #     dados_novos=reserva.__dict__,
        #     usuario_id=usuario_id,
        #     ip_address="",
        # )

        # Envia notificações
        usuario = self.usuario_repository.get_by_id(usuario_id)
        self.email_service.notificar_reserva_criada(reserva, usuario)

        return reserva

    def delete(self, reserva_id: UUID, usuario_id: UUID) -> None:
        """Remove uma reserva"""
        # Busca a reserva
        reserva = self.reserva_repository.get_by_id(reserva_id)
        if not reserva:
            raise NotFoundException(f"Reserva com ID {reserva_id} não encontrada")

        # Verifica se o usuário é o dono da reserva
        if reserva.usuario_id != usuario_id:
            raise BusinessException("Você não tem permissão para remover esta reserva, pois não é o dono da reserva")

        # Remove a reserva
        self.reserva_repository.delete(reserva_id)

    def get_by_query(self, filtros: ReservaFiltros) -> ReservasPaginadas:
        """Busca reservas com filtros e paginação"""
        return self.reserva_repository.get_by_query(filtros)

    def get_by_usuario(self, usuario_id: UUID) -> List[Reserva]:
        """Busca todas as reservas de um usuário"""
        return self.reserva_repository.get_by_usuario(usuario_id)

    def get_by_sala(self, sala_id: UUID) -> List[Reserva]:
        """Busca todas as reservas de uma sala"""
        return self.reserva_repository.get_by_sala(sala_id)

    def _validar_datas(self, inicio: datetime, fim: datetime) -> None:
        """Valida as datas de início e fim da reserva"""
        if inicio >= fim:
            raise BusinessException("Data de início deve ser anterior à data de fim")

        if DateTimeUtils.is_past(inicio):
            raise BusinessException(
                "Não é possível criar/atualizar reservas para datas passadas"
            )

    def _verificar_conflitos(self, reserva_data: ReservaCreate, reserva_id: UUID = None) -> None:
        """
        Verifica se há conflitos de horário para a sala.
        """
        # Normaliza as datas de entrada para UTC sem timezone
        inicio = reserva_data.inicio.replace(tzinfo=None)
        fim = reserva_data.fim.replace(tzinfo=None)
        
        # Busca reservas existentes para a sala no mesmo dia
        reservas_existentes = self.reserva_repository.get_by_sala_and_date(
            reserva_data.sala_id, inicio.date()
        )

        # Verifica conflitos
        for reserva in reservas_existentes:
            # Normaliza as datas da reserva existente
            reserva_inicio = reserva.inicio.replace(tzinfo=None)
            reserva_fim = reserva.fim.replace(tzinfo=None)
            
            # Ignora a própria reserva ao atualizar
            if reserva_id and reserva.id == reserva_id:
                continue
                
            # Verifica se há sobreposição de horários
            if (
                (inicio >= reserva_inicio and inicio < reserva_fim) or      # Início dentro do período
                (fim > reserva_inicio and fim <= reserva_fim) or           # Fim dentro do período
                (inicio <= reserva_inicio and fim >= reserva_fim) or       # Período engloba
                (inicio == reserva_inicio and fim == reserva_fim)          # Período idêntico
            ):
                raise BusinessException(
                    f"Conflito de horário: A sala já está reservada das "
                    f"{reserva.inicio.strftime('%H:%M')} às {reserva.fim.strftime('%H:%M')}. "
                    f"Não é possível fazer uma reserva que se sobreponha a este período."
                )

    def _check_recorrente_conflict(
        self, inicio: datetime, fim: datetime, reserva_recorrente: ReservaRecorrente
    ) -> bool:
        """Verifica se existe conflito com uma reserva recorrente"""
        if (
            inicio.date() > reserva_recorrente.data_fim
            or fim.date() < reserva_recorrente.data_inicio
        ):
            return False

        if inicio.date() < reserva_recorrente.data_inicio:
            inicio_recorrente = datetime.combine(
                reserva_recorrente.data_inicio, reserva_recorrente.hora_inicio
            )
        else:
            inicio_recorrente = inicio

        if fim.date() > reserva_recorrente.data_fim:
            fim_recorrente = datetime.combine(
                reserva_recorrente.data_fim, reserva_recorrente.hora_fim
            )
        else:
            fim_recorrente = fim

        return (
            inicio_recorrente.weekday() in reserva_recorrente.dia_da_semana
            and inicio_recorrente.time() < reserva_recorrente.hora_fim
            and fim_recorrente.time() > reserva_recorrente.hora_inicio
        )
