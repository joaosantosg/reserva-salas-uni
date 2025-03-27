from uuid import UUID
from datetime import date, time, timedelta, datetime
from typing import List, Optional
import holidays

from app.repository.reserva_repository import ReservaRepository
from app.repository.reserva_recorrente_repository import ReservaRecorrenteRepository
from app.core.commons.exceptions import NotFoundException, BusinessException, ConflictException
from app.model.reserva_recorrente_model import ReservaRecorrente
from app.model.reserva_model import Reserva
from app.schema.reserva_schema import (
    ReservaRecorrenteCreate,
    ReservaRecorrenteUpdate,
    ReservaRecorrenteFiltros,
    ReservasRecorrentesPaginadas
)
from app.util.datetime_utils import DateTimeUtils
from app.schema.reserva_schema import FrequenciaRecorrencia
from app.services.email_service import EmailService
from app.repository.sala_repository import SalaRepository
from app.repository.usuario_repository import UsuarioRepository


class ReservaRecorrenteService:
    """Serviço responsável pela gestão de reservas recorrentes"""
    
    def __init__(self, reserva_repository: ReservaRepository, 
                 reserva_recorrente_repository: ReservaRecorrenteRepository, 
                 sala_repository: SalaRepository, 
                 usuario_repository: UsuarioRepository, 
                 email_service: EmailService):
        self.reserva_repository = reserva_repository
        self.reserva_recorrente_repository = reserva_recorrente_repository
        self.sala_repository = sala_repository
        self.usuario_repository = usuario_repository

        self.email_service = email_service
        self.feriados = holidays.BR()

    def get_by_id(self, reserva_id: UUID) -> ReservaRecorrente:
        """Busca uma reserva recorrente pelo ID"""
        reserva = self.reserva_recorrente_repository.get_by_id(reserva_id)
        if not reserva:
            raise NotFoundException(f"Reserva recorrente com ID {reserva_id} não encontrada")
        return reserva

    def create(self, reserva_data: ReservaRecorrenteCreate, usuario_id: UUID) -> ReservaRecorrente:
        """Cria uma nova reserva recorrente e gera as reservas individuais"""
        # Busca a sala
        sala = self.sala_repository.get_by_id(reserva_data.sala_id)
        if not sala:
            raise NotFoundException(f"Sala com ID {reserva_data.sala_id} não encontrada")
        
        # Busca o usuário
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundException(f"Usuário com ID {usuario_id} não encontrado")
        
        # Validações
        self._validar_datas(reserva_data.data_inicio, reserva_data.data_fim)
        self._validar_horarios(reserva_data.hora_inicio, reserva_data.hora_fim)
        self._validar_dias_semana(reserva_data.dia_da_semana, reserva_data.frequencia)
        self._verificar_conflitos(reserva_data)
        self._validar_feriados(reserva_data)

        # Criar a reserva recorrente
        reserva_recorrente = ReservaRecorrente(**reserva_data.model_dump())
        reserva_recorrente.semestre = self._get_semestre(reserva_data.data_inicio)
        reserva_recorrente.ano = reserva_data.data_inicio.year
        reserva_recorrente = self.reserva_recorrente_repository.save(reserva_recorrente)

        # Gerar as reservas individuais
        self._gerar_reservas_individuais(reserva_recorrente)
        
        # Envia notificações
        self.email_service.notificar_reserva_recorrente_criada(reserva_recorrente, usuario)

        return reserva_recorrente

    def update(self, reserva_id: UUID, reserva_data: ReservaRecorrenteUpdate) -> ReservaRecorrente:
        """Atualiza uma reserva recorrente existente"""
        reserva = self.get_by_id(reserva_id)
        
        if reserva_data.data_inicio and reserva_data.data_fim:
            self._validar_datas(reserva_data.data_inicio, reserva_data.data_fim)
            
        if reserva_data.hora_inicio and reserva_data.hora_fim:
            self._validar_horarios(reserva_data.hora_inicio, reserva_data.hora_fim)
            
        if reserva_data.dia_da_semana:
            self._validar_dias_semana(reserva_data.dia_da_semana, reserva_data.frequencia)

        # Verificar conflitos se houver alterações relevantes
        if any([
            reserva_data.data_inicio,
            reserva_data.data_fim,
            reserva_data.hora_inicio,
            reserva_data.hora_fim,
            reserva_data.dia_da_semana
        ]):
            data_inicio = reserva_data.data_inicio or reserva.data_inicio
            data_fim = reserva_data.data_fim or reserva.data_fim
            hora_inicio = reserva_data.hora_inicio or reserva.hora_inicio
            hora_fim = reserva_data.hora_fim or reserva.hora_fim
            dia_da_semana = reserva_data.dia_da_semana or reserva.dia_da_semana
            
            create_data = ReservaRecorrenteCreate(
                sala_id=reserva.sala_id,
                usuario_id=reserva.usuario_id,
                motivo=reserva_data.motivo or reserva.motivo,
                frequencia=reserva_data.frequencia or reserva.frequencia,
                dia_da_semana=dia_da_semana,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                data_inicio=data_inicio,
                data_fim=data_fim,
                excecoes=reserva_data.excecoes or reserva.excecoes
            )
            
            self._verificar_conflitos(create_data, exclude_id=reserva_id)
            self._validar_feriados(create_data)

        return self.reserva_recorrente_repository.update(reserva_id, reserva_data)

    def delete(self, reserva_id: UUID, usuario_id: UUID) -> ReservaRecorrente:
        """Remove uma reserva recorrente e suas reservas individuais (soft delete)"""
        reserva = self.get_by_id(reserva_id)
        if reserva.data_inicio < date.today():
            raise BusinessException("Não é possível excluir reservas recorrentes passadas")

        # Soft delete da reserva recorrente
        reserva.ativo = False
        reserva.excluido_em = DateTimeUtils.now()
        reserva.excluido_por = usuario_id
        self.reserva_recorrente_repository.update(reserva_id, reserva)

        # Soft delete das reservas individuais
        self.reserva_repository.soft_delete_reservas_recorrentes(reserva_id, usuario_id)

        return reserva

    def recriar_reservas(self, reserva_id: UUID) -> ReservaRecorrente:
        """Recria as reservas individuais de uma reserva recorrente"""
        reserva = self.get_by_id(reserva_id)
        if not reserva.ativo:
            raise BusinessException("Não é possível recriar reservas de uma reserva recorrente inativa")

        # Soft delete das reservas existentes
        self.reserva_repository.soft_delete_reservas_recorrentes(reserva_id, reserva.usuario_id)

        # Recriar as reservas
        self._gerar_reservas_individuais(reserva)

        return reserva

    def get_by_query(self, filtros: ReservaRecorrenteFiltros) -> ReservasRecorrentesPaginadas:
        """Busca reservas recorrentes com filtros e paginação"""
        return self.reserva_recorrente_repository.get_by_query(filtros)

    def _validar_datas(self, data_inicio: date, data_fim: date) -> None:
        """Valida as datas de início e fim da reserva recorrente"""
        if data_inicio >= data_fim:
            raise BusinessException("Data de início deve ser anterior à data de fim")
        
        print(f"data_inicio: {data_inicio}, data_fim: {data_fim}")
        print(f"date.today(): {date.today()}")
        if data_inicio < date.today():
            raise BusinessException("Não é possível criar/atualizar reservas recorrentes para datas passadas")

    def _validar_horarios(self, hora_inicio: time, hora_fim: time) -> None:
        """Valida os horários de início e fim da reserva recorrente"""
        if hora_inicio >= hora_fim:
            raise BusinessException("Hora de início deve ser anterior à hora de fim")

    def _validar_dias_semana(self, dias_semana: List[int], frequencia: FrequenciaRecorrencia) -> None:
        """Valida os dias da semana da reserva recorrente"""
        if frequencia == FrequenciaRecorrencia.SEMANAL:
            if not dias_semana:
                raise BusinessException("Para frequência semanal, é necessário informar os dias da semana")
            if not all(0 <= dia <= 6 for dia in dias_semana):
                raise BusinessException("Dias da semana devem estar entre 0 (segunda) e 6 (domingo)")
        elif frequencia == FrequenciaRecorrencia.DIARIA:
            # Para frequência diária, não é necessário validar dias da semana
            pass

    def _verificar_conflitos(self, reserva_data: ReservaRecorrenteCreate, exclude_id: Optional[UUID] = None) -> None:
        """Verifica conflitos de horário"""
        if self.reserva_recorrente_repository.check_conflict(
            reserva_data.sala_id,
            reserva_data.data_inicio,
            reserva_data.data_fim,
            reserva_data.hora_inicio,
            reserva_data.hora_fim,
            reserva_data.dia_da_semana,
            exclude_id
        ):
            raise ConflictException("Já existe uma reserva recorrente para este horário")

    def _validar_feriados(self, reserva_data: ReservaRecorrenteCreate) -> None:
        """Valida se os dias selecionados não caem em feriados nacionais"""
        data_atual = reserva_data.data_inicio
        while data_atual <= reserva_data.data_fim:
            # Para frequência diária, verifica todos os dias
            # Para frequência semanal, verifica apenas os dias selecionados
            if (reserva_data.frequencia == FrequenciaRecorrencia.DIARIA or 
                (reserva_data.dia_da_semana and data_atual.weekday() in reserva_data.dia_da_semana)):
                # Verifica se é feriado
                if data_atual in self.feriados:
                    print(f"A data {data_atual.strftime('%d/%m/%Y')} é um feriado nacional: {self.feriados[data_atual]}")
                    # Adiciona a data ao array de exceções
                    if not reserva_data.excecoes:
                        reserva_data.excecoes = []
                    reserva_data.excecoes.append(data_atual)
            data_atual = data_atual + timedelta(days=1)

    def _gerar_reservas_individuais(self, reserva_recorrente: ReservaRecorrente) -> None:
        """
        Gera as reservas individuais para uma reserva recorrente.
        Salva em lotes de 500 para melhor performance.
        """
        data_atual = reserva_recorrente.data_inicio
        lote_reservas = []
        TAMANHO_LOTE = 500

        while data_atual <= reserva_recorrente.data_fim:
            deve_criar = False
            
            # Verifica se deve criar reserva baseado na frequência
            if reserva_recorrente.frequencia == FrequenciaRecorrencia.DIARIA:
                deve_criar = True
            elif reserva_recorrente.frequencia == FrequenciaRecorrencia.SEMANAL:
                deve_criar = data_atual.weekday() in reserva_recorrente.dia_da_semana
            elif reserva_recorrente.frequencia == FrequenciaRecorrencia.MENSAL:
                deve_criar = data_atual.day == reserva_recorrente.dia_do_mes

            # Verifica exceções e feriados
            if deve_criar and data_atual not in reserva_recorrente.excecoes and data_atual not in self.feriados:
                inicio = datetime.combine(data_atual, reserva_recorrente.hora_inicio)
                fim = datetime.combine(data_atual, reserva_recorrente.hora_fim)

                reserva = Reserva(
                    sala_id=reserva_recorrente.sala_id,
                    usuario_id=reserva_recorrente.usuario_id,
                    inicio=inicio,
                    fim=fim,
                    motivo=reserva_recorrente.motivo,
                    reserva_recorrente_id=reserva_recorrente.id
                )
                lote_reservas.append(reserva)

                if len(lote_reservas) >= TAMANHO_LOTE:
                    self._salvar_lote_reservas(lote_reservas)
                    lote_reservas = []

            data_atual += timedelta(days=1)

        if lote_reservas:
            self._salvar_lote_reservas(lote_reservas)

    def _salvar_lote_reservas(self, reservas: List[Reserva]) -> None:
        """
        Salva um lote de reservas de uma vez usando bulk_save_objects.
        """
        try:
            self.reserva_repository.session.bulk_save_objects(reservas)
            self.reserva_repository.session.commit()
        except Exception as e:
            self.reserva_repository.session.rollback()
            raise BusinessException(f"Erro ao salvar lote de reservas: {str(e)}")

    def _get_semestre(self, data: date) -> int:
        """Retorna o semestre (1 ou 2) baseado na data"""
        return 1 if data.month <= 6 else 2 

    def _validar_frequencia(self, frequencia: FrequenciaRecorrencia, dia_da_semana: List[int], dia_do_mes: int) -> None:
        """Valida os campos específicos de cada frequência"""
        if frequencia == FrequenciaRecorrencia.SEMANAL:
            if not dia_da_semana:
                raise BusinessException("Para frequência semanal, é necessário informar os dias da semana")
            if not all(0 <= dia <= 6 for dia in dia_da_semana):
                raise BusinessException("Dias da semana devem estar entre 0 (segunda) e 6 (domingo)")
        elif frequencia == FrequenciaRecorrencia.MENSAL:
            if not dia_do_mes:
                raise BusinessException("Para frequência mensal, é necessário informar o dia do mês")
            if not 1 <= dia_do_mes <= 31:
                raise BusinessException("Dia do mês deve estar entre 1 e 31") 
        elif frequencia == FrequenciaRecorrencia.DIARIA:
            if not dia_da_semana:
                raise BusinessException("Para frequência diária, é necessário informar os dias da semana")
            if not all(0 <= dia <= 6 for dia in dia_da_semana):
                raise BusinessException("Dias da semana devem estar entre 0 (segunda) e 6 (domingo)")
            
            