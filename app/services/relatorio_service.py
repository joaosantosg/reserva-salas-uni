from datetime import datetime
from app.repository.reserva_repository import ReservaRepository


class RelatorioService:
    """Serviço responsável pela geração de relatórios"""

    def __init__(self, reserva_repository: ReservaRepository):
        self.reserva_repository = reserva_repository

    def gerar_relatorio_uso_salas(
        self, data_inicio: datetime, data_fim: datetime
    ) -> dict:
        """
        Gera relatório com estatísticas de uso das salas.
        Inclui:
        - Total de reservas por sala
        - Horários de pico
        - Taxa de ocupação
        """
        # Busca todas as reservas no período
        reservas = self.reserva_repository.get_by_date_range(data_inicio, data_fim)

        # Estatísticas por sala
        stats_por_sala = {}
        for reserva in reservas:
            sala_id = reserva.sala_id
            if sala_id not in stats_por_sala:
                stats_por_sala[sala_id] = {
                    "total_reservas": 0,
                    "horas_reservadas": 0,
                    "horarios_pico": {},
                    "sala": reserva.sala,
                }

            stats = stats_por_sala[sala_id]
            stats["total_reservas"] += 1

            # Calcula duração em horas
            duracao = (reserva.fim - reserva.inicio).total_seconds() / 3600
            stats["horas_reservadas"] += duracao

            # Conta horários de pico
            hora_inicio = reserva.inicio.hour
            if hora_inicio not in stats["horarios_pico"]:
                stats["horarios_pico"][hora_inicio] = 0
            stats["horarios_pico"][hora_inicio] += 1

        # Calcula taxa de ocupação
        periodo_total = (data_fim - data_inicio).total_seconds() / 3600  # horas
        for stats in stats_por_sala.values():
            stats["taxa_ocupacao"] = (stats["horas_reservadas"] / periodo_total) * 100

        # Ordena salas por total de reservas
        salas_ordenadas = sorted(
            stats_por_sala.values(), key=lambda x: x["total_reservas"], reverse=True
        )

        return {
            "periodo": {"inicio": data_inicio, "fim": data_fim},
            "total_salas": len(stats_por_sala),
            "salas": salas_ordenadas,
            "resumo": {
                "total_reservas": sum(
                    s["total_reservas"] for s in stats_por_sala.values()
                ),
                "media_ocupacao": sum(
                    s["taxa_ocupacao"] for s in stats_por_sala.values()
                )
                / len(stats_por_sala)
                if stats_por_sala
                else 0,
            },
        }
