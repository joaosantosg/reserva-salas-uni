from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from app.repository.reserva_repository import ReservaRepository
from app.repository.sala_repository import SalaRepository
from app.repository.usuario_repository import UsuarioRepository
from app.model.reserva_model import Reserva
from app.model.sala_model import Sala
from app.model.usuario_model import Usuario
from app.schema.relatorio_schema import (
    ReservasPorSalaResponse,
    ReservasPorUsuarioResponse,
    ReservasPorPeriodoResponse,
    OcupacaoPorSalaResponse,
    DashboardStatsResponse,
)
import logging

logger = logging.getLogger(__name__)

class ReportsService:
    """Serviço responsável pela geração de relatórios"""

    def __init__(
        self,
        reserva_repository: ReservaRepository,
        sala_repository: SalaRepository,
        usuario_repository: UsuarioRepository,
    ):
        self.reserva_repository = reserva_repository
        self.sala_repository = sala_repository
        self.usuario_repository = usuario_repository

    def get_dashboard_stats(self) -> DashboardStatsResponse:
        """Retorna estatísticas gerais para o dashboard"""
        try:
            hoje = date.today()
            inicio_semana = hoje - timedelta(days=hoje.weekday())
            inicio_mes = hoje.replace(day=1)

            # Totais gerais
            total_reservas = self.reserva_repository.count_all()
            total_salas = self.sala_repository.count_all()
            total_usuarios = self.usuario_repository.count_all()

            # Reservas por período
            reservas_hoje = self.reserva_repository.count_by_date(hoje)
            reservas_semana = self.reserva_repository.count_by_date_range(inicio_semana, hoje)
            reservas_mes = self.reserva_repository.count_by_date_range(inicio_mes, hoje)

            # Top 5 salas mais ocupadas
            salas_mais_ocupadas = self._get_salas_mais_ocupadas(hoje - timedelta(days=30), hoje)

            # Top 5 usuários mais ativos
            usuarios_mais_ativos = self._get_usuarios_mais_ativos(hoje - timedelta(days=30), hoje)

            return DashboardStatsResponse(
                total_reservas=total_reservas,
                total_salas=total_salas,
                total_usuarios=total_usuarios,
                reservas_hoje=reservas_hoje,
                reservas_semana=reservas_semana,
                reservas_mes=reservas_mes,
                salas_mais_ocupadas=salas_mais_ocupadas,
                usuarios_mais_ativos=usuarios_mais_ativos,
            )

        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas do dashboard: {str(e)}")
            raise

    def get_reservas_por_sala(
        self, data_inicio: date, data_fim: date
    ) -> List[ReservasPorSalaResponse]:
        """Retorna quantidade de reservas por sala em um período"""
        try:
            salas = self.sala_repository.get_all()
            reservas_por_sala = []

            for sala in salas:
                quantidade = self.reserva_repository.count_by_sala_and_date_range(
                    sala.id, data_inicio, data_fim
                )
                reservas_por_sala.append(
                    ReservasPorSalaResponse(
                        sala=sala,
                        quantidade=quantidade,
                        periodo_inicio=data_inicio,
                        periodo_fim=data_fim,
                    )
                )

            return reservas_por_sala

        except Exception as e:
            logger.error(f"Erro ao gerar relatório de reservas por sala: {str(e)}")
            raise

    def get_reservas_por_usuario(
        self, data_inicio: date, data_fim: date
    ) -> List[ReservasPorUsuarioResponse]:
        """Retorna quantidade de reservas por usuário em um período"""
        try:
            usuarios = self.usuario_repository.get_all()
            reservas_por_usuario = []

            for usuario in usuarios:
                quantidade = self.reserva_repository.count_by_usuario_and_date_range(
                    usuario.id, data_inicio, data_fim
                )
                reservas_por_usuario.append(
                    ReservasPorUsuarioResponse(
                        usuario=usuario,
                        quantidade=quantidade,
                        periodo_inicio=data_inicio,
                        periodo_fim=data_fim,
                    )
                )

            return reservas_por_usuario

        except Exception as e:
            logger.error(f"Erro ao gerar relatório de reservas por usuário: {str(e)}")
            raise

    def get_reservas_por_periodo(
        self, sala_id: str, data_inicio: date, data_fim: date
    ) -> List[ReservasPorPeriodoResponse]:
        """Retorna quantidade de reservas por período para uma sala específica"""
        try:
            reservas = self.reserva_repository.get_by_sala_and_date_range(
                sala_id, data_inicio, data_fim
            )
            
            # Agrupa reservas por data
            reservas_por_data = {}
            for reserva in reservas:
                data = reserva.inicio.date()
                if data not in reservas_por_data:
                    reservas_por_data[data] = 0
                reservas_por_data[data] += 1

            # Cria lista de respostas
            return [
                ReservasPorPeriodoResponse(
                    data=data,
                    quantidade=quantidade,
                    sala_id=sala_id,
                )
                for data, quantidade in reservas_por_data.items()
            ]

        except Exception as e:
            logger.error(f"Erro ao gerar relatório de reservas por período: {str(e)}")
            raise

    def get_ocupacao_por_sala(self, data: date) -> List[OcupacaoPorSalaResponse]:
        """Retorna taxa de ocupação por sala em uma data específica"""
        try:
            salas = self.sala_repository.get_all()
            ocupacao_por_sala = []

            for sala in salas:
                # Busca reservas do dia
                reservas = self.reserva_repository.get_by_sala_and_date(sala.id, data)
                
                # Calcula horas reservadas
                total_horas = sum(
                    (reserva.fim - reserva.inicio).total_seconds() / 3600
                    for reserva in reservas
                )
                
                # Horas disponíveis (8h - 22h = 14h)
                total_horas_disponiveis = 14
                
                # Calcula taxa de ocupação
                taxa_ocupacao = (total_horas / total_horas_disponiveis) * 100

                ocupacao_por_sala.append(
                    OcupacaoPorSalaResponse(
                        sala=sala,
                        taxa_ocupacao=taxa_ocupacao,
                        data=data,
                        total_horas=total_horas,
                        total_horas_disponiveis=total_horas_disponiveis,
                    )
                )

            return ocupacao_por_sala

        except Exception as e:
            logger.error(f"Erro ao gerar relatório de ocupação por sala: {str(e)}")
            raise

    def _get_salas_mais_ocupadas(
        self, data_inicio: date, data_fim: date, limit: int = 5
    ) -> List[ReservasPorSalaResponse]:
        """Retorna as salas mais ocupadas em um período"""
        salas = self.get_reservas_por_sala(data_inicio, data_fim)
        return sorted(salas, key=lambda x: x.quantidade, reverse=True)[:limit]

    def _get_usuarios_mais_ativos(
        self, data_inicio: date, data_fim: date, limit: int = 5
    ) -> List[ReservasPorUsuarioResponse]:
        """Retorna os usuários mais ativos em um período"""
        usuarios = self.get_reservas_por_usuario(data_inicio, data_fim)
        return sorted(usuarios, key=lambda x: x.quantidade, reverse=True)[:limit] 