from datetime import datetime, date, timedelta
from typing import List
from sqlalchemy.orm import Session

from app.model.reserva_recorrente_model import ReservaRecorrente
from app.model.reserva_model import Reserva
from app.repository.reserva_repository import ReservaRepository
from app.repository.reserva_recorrente_repository import ReservaRecorrenteRepository
from app.schema.reserva_schema import ReservaCreate

class ReservaRecorrenteJob:
    """Serviço responsável por criar reservas baseadas em reservas recorrentes"""
    
    def __init__(self, session: Session):
        self.session = session
        self.reserva_repository = ReservaRepository(session)
        self.reserva_recorrente_repository = ReservaRecorrenteRepository(session)

    def processar_reservas_recorrentes(self, data_inicio: date = None, data_fim: date = None):
        """
        Processa todas as reservas recorrentes ativas e cria as reservas individuais.
        
        Args:
            data_inicio: Data inicial para criar reservas (default: hoje)
            data_fim: Data final para criar reservas (default: hoje + 30 dias)
        """
        if data_inicio is None:
            data_inicio = date.today()
        if data_fim is None:
            data_fim = date.today() + timedelta(days=30)

        # Busca todas as reservas recorrentes ativas
        reservas_recorrentes = self.reserva_recorrente_repository.get_active_by_period(
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        for reserva_recorrente in reservas_recorrentes:
            self._criar_reservas_para_recorrencia(reserva_recorrente, data_inicio, data_fim)

    def _criar_reservas_para_recorrencia(
        self,
        reserva_recorrente: ReservaRecorrente,
        data_inicio: date,
        data_fim: date
    ):
        """
        Cria as reservas individuais para uma reserva recorrente.
        
        Args:
            reserva_recorrente: Reserva recorrente a ser processada
            data_inicio: Data inicial para criar reservas
            data_fim: Data final para criar reservas
        """
        data_atual = data_inicio
        while data_atual <= data_fim:
            # Verifica se a data está dentro do período da reserva recorrente
            if data_atual < reserva_recorrente.data_inicio or data_atual > reserva_recorrente.data_fim:
                data_atual += timedelta(days=1)
                continue

            # Verifica se a data é uma exceção
            if data_atual in reserva_recorrente.excecoes:
                data_atual += timedelta(days=1)
                continue

            # Verifica se deve criar reserva para este dia
            if self._deve_criar_reserva(reserva_recorrente, data_atual):
                self._criar_reserva_individual(reserva_recorrente, data_atual)

            data_atual += timedelta(days=1)

    def _deve_criar_reserva(self, reserva_recorrente: ReservaRecorrente, data: date) -> bool:
        """
        Verifica se deve criar uma reserva para a data especificada.
        
        Args:
            reserva_recorrente: Reserva recorrente
            data: Data a ser verificada
            
        Returns:
            bool: True se deve criar reserva, False caso contrário
        """
        if reserva_recorrente.frequencia == "DIARIA":
            return True
        
        if reserva_recorrente.frequencia == "SEMANAL":
            return data.weekday() in reserva_recorrente.dia_da_semana
        
        if reserva_recorrente.frequencia == "MENSAL":
            return data.day == reserva_recorrente.dia_da_semana[0]
        
        return False

    def _criar_reserva_individual(self, reserva_recorrente: ReservaRecorrente, data: date):
        """
        Cria uma reserva individual para uma data específica.
        
        Args:
            reserva_recorrente: Reserva recorrente
            data: Data para criar a reserva
        """
        # Verifica se já existe uma reserva para esta data e sala
        if self.reserva_repository.check_conflict(
            sala_id=reserva_recorrente.sala_id,
            inicio=datetime.combine(data, reserva_recorrente.hora_inicio),
            fim=datetime.combine(data, reserva_recorrente.hora_fim)
        ):
            return  # Já existe uma reserva para este horário

        # Cria a reserva individual
        reserva = ReservaCreate(
            sala_id=reserva_recorrente.sala_id,
            inicio=datetime.combine(data, reserva_recorrente.hora_inicio),
            fim=datetime.combine(data, reserva_recorrente.hora_fim),
            usuario_id=reserva_recorrente.usuario_id,
            motivo=f"{reserva_recorrente.motivo} (Recorrente: {reserva_recorrente.motivo})"
        )
        
        self.reserva_repository.create(reserva)

