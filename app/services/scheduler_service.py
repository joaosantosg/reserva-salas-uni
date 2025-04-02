from datetime import datetime, date
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.repository.reserva_repository import ReservaRepository
from app.repository.usuario_repository import UsuarioRepository
from app.services.email_service import EmailService
from app.model.reserva_model import Reserva
from app.model.usuario_model import Usuario
from app.util.datetime_utils import DateTimeUtils
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    """Serviço responsável pelo agendamento de tarefas"""

    def __init__(
        self,
        reserva_repository: ReservaRepository,
        usuario_repository: UsuarioRepository,
        email_service: EmailService,
    ):
        self.reserva_repository = reserva_repository
        self.usuario_repository = usuario_repository
        self.email_service = email_service
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Inicia o scheduler"""
        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self):
        """Para o scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    def schedule_daily_notifications(self):
        """Agenda a tarefa de notificação diária"""
        # Agenda para rodar todo dia às 00:00
        self.scheduler.add_job(
            self._send_daily_notifications,
            CronTrigger(hour=0, minute=0),
            id="daily_notifications",
            name="Enviar notificações diárias de reservas",
            replace_existing=True,
        )
        logger.info("Daily notifications scheduled")

    async def _send_daily_notifications(self):
        """Envia notificações para as reservas do dia"""
        try:
            today = date.today()
            logger.info(f"Enviando notificações para reservas do dia {today}")

            # Busca todas as reservas do dia
            reservas = self.reserva_repository.get_by_date(today)
            
            if not reservas:
                logger.info("Nenhuma reserva encontrada para hoje")
                return

            # Agrupa reservas por usuário
            reservas_por_usuario = {}
            for reserva in reservas:
                usuario = self.usuario_repository.get_by_id(reserva.usuario_id)
                if usuario:
                    if usuario.id not in reservas_por_usuario:
                        reservas_por_usuario[usuario.id] = []
                    reservas_por_usuario[usuario.id].append(reserva)

            # Envia email para cada usuário com suas reservas
            for usuario_id, reservas_usuario in reservas_por_usuario.items():
                usuario = self.usuario_repository.get_by_id(usuario_id)
                if usuario:
                    self._send_user_notifications(usuario, reservas_usuario)

            logger.info(f"Notificações enviadas com sucesso para {len(reservas_por_usuario)} usuários")

        except Exception as e:
            logger.error(f"Erro ao enviar notificações diárias: {str(e)}")

    def _send_user_notifications(self, usuario: Usuario, reservas: List[Reserva]):
        """Envia notificações para um usuário específico"""
        try:
            subject = f"Suas reservas para hoje ({DateTimeUtils.format_datetime(datetime.now(), '%d/%m/%Y')})"
            
            text = f"Olá {usuario.nome},\n\n"
            text += "Você tem as seguintes reservas para hoje:\n\n"
            
            for reserva in reservas:
                text += f"- Sala: {reserva.sala.identificacao_sala}\n"
                text += f"  Horário: {DateTimeUtils.format_datetime(reserva.inicio, '%H:%M')} - {DateTimeUtils.format_datetime(reserva.fim, '%H:%M')}\n"
                text += f"  Motivo: {reserva.motivo}\n\n"

            text += "Atenciosamente,\nSistema de Reserva de Salas"

            html = f"""
            <html>
                <body>
                    <h2>Suas reservas para hoje</h2>
                    <p>Olá {usuario.nome},</p>
                    <p>Você tem as seguintes reservas para hoje:</p>
                    <ul>
            """

            for reserva in reservas:
                html += f"""
                        <li>
                            <strong>Sala:</strong> {reserva.sala.identificacao_sala}<br>
                            <strong>Horário:</strong> {DateTimeUtils.format_datetime(reserva.inicio, '%H:%M')} - {DateTimeUtils.format_datetime(reserva.fim, '%H:%M')}<br>
                            <strong>Motivo:</strong> {reserva.motivo}
                        </li>
                """

            html += """
                    </ul>
                    <p>Atenciosamente,<br>Sistema de Reserva de Salas</p>
                </body>
            </html>
            """

            self.email_service.email_client.send_email(
                to_email=usuario.email,
                subject=subject,
                text=text,
                html=html,
            )

            logger.info(f"Notificação enviada com sucesso para {usuario.email}")

        except Exception as e:
            logger.error(f"Erro ao enviar notificação para {usuario.email}: {str(e)}") 