from datetime import datetime
from typing import Dict, Any
from app.clients.email_client import EmailClient
from app.model.reserva_model import Reserva
from app.model.reserva_recorrente_model import ReservaRecorrente
from app.model.usuario_model import Usuario


class EmailService:
    """Serviço responsável pelo envio de emails de notificação"""

    def __init__(self, email_client: EmailClient):
        self.email_client = email_client

    def _format_date(self, date: datetime) -> str:
        """Formata uma data para exibição no email"""
        return date.strftime("%d/%m/%Y")

    def _format_time(self, date: datetime) -> str:
        """Formata um horário para exibição no email"""
        return date.strftime("%H:%M")

    def _get_reserva_template_data(
        self, reserva: Reserva, usuario: Usuario
    ) -> Dict[str, Any]:
        """Gera os dados para o template de email de reserva"""
        return {
            "nome": usuario.nome,
            "sala": reserva.sala.identificacao_sala,
            "bloco": reserva.sala.bloco.nome,
            "data": self._format_date(reserva.inicio),
            "hora_inicio": self._format_time(reserva.inicio),
            "hora_fim": self._format_time(reserva.fim),
            "motivo": reserva.motivo,
        }

    def _get_reserva_recorrente_template_data(
        self, reserva: ReservaRecorrente, usuario: Usuario
    ) -> Dict[str, Any]:
        """Gera os dados para o template de email de reserva recorrente"""
        return {
            "nome": usuario.nome,
            "sala": reserva.sala.identificacao_sala,
            "bloco": reserva.sala.bloco.nome,
            "data_inicio": self._format_date(reserva.data_inicio),
            "data_fim": self._format_date(reserva.data_fim),
            "hora_inicio": reserva.hora_inicio.strftime("%H:%M"),
            "hora_fim": reserva.hora_fim.strftime("%H:%M"),
            "frequencia": reserva.frequencia.value,
            "motivo": reserva.motivo,
        }

    def notificar_reserva_criada(self, reserva: Reserva, usuario: Usuario) -> None:
        """Envia notificação de nova reserva criada"""
        template_data = self._get_reserva_template_data(reserva, usuario)

        subject = f"Nova reserva de sala - {reserva.sala.identificacao_sala}"
        text = (
            f"Olá {usuario.nome},\n\n"
            f"Sua reserva foi criada com sucesso!\n\n"
            f"Detalhes da reserva:\n"
            f"Sala: {reserva.sala.identificacao_sala}\n"
            f"Bloco: {reserva.sala.bloco.nome}\n"
            f"Data: {self._format_date(reserva.inicio)}\n"
            f"Horário: {self._format_time(reserva.inicio)} - {self._format_time(reserva.fim)}\n"
            f"Motivo: {reserva.motivo}\n\n"
            f"Atenciosamente,\n"
            f"Sistema de Reserva de Salas"
        )

        html = f"""
        <html>
            <body>
                <h2>Nova reserva criada</h2>
                <p>Olá {usuario.nome},</p>
                <p>Sua reserva foi criada com sucesso!</p>
                <h3>Detalhes da reserva:</h3>
                <ul>
                    <li><strong>Sala:</strong> {reserva.sala.identificacao_sala}</li>
                    <li><strong>Bloco:</strong> {reserva.sala.bloco.nome}</li>
                    <li><strong>Data:</strong> {self._format_date(reserva.inicio)}</li>
                    <li><strong>Horário:</strong> {self._format_time(reserva.inicio)} - {self._format_time(reserva.fim)}</li>
                    <li><strong>Motivo:</strong> {reserva.motivo}</li>
                </ul>
                <p>Atenciosamente,<br>Sistema de Reserva de Salas</p>
            </body>
        </html>
        """

        self.email_client.send_email(
            to_email=usuario.email,
            subject=subject,
            text=text,
            html=html,
            template_data=template_data,
        )

    def notificar_reserva_recorrente_criada(
        self, reserva: ReservaRecorrente, usuario: Usuario
    ) -> None:
        """Envia notificação de nova reserva recorrente criada"""
        template_data = self._get_reserva_recorrente_template_data(reserva, usuario)

        subject = f"Nova reserva recorrente - {reserva.sala.identificacao_sala}"
        text = (
            f"Olá {usuario.nome},\n\n"
            f"Sua reserva recorrente foi criada com sucesso!\n\n"
            f"Detalhes da reserva:\n"
            f"Sala: {reserva.sala.identificacao_sala}\n"
            f"Bloco: {reserva.sala.bloco.nome}\n"
            f"Período: {self._format_date(reserva.data_inicio)} a {self._format_date(reserva.data_fim)}\n"
            f"Horário: {reserva.hora_inicio.strftime('%H:%M')} - {reserva.hora_fim.strftime('%H:%M')}\n"
            f"Frequência: {reserva.frequencia.value}\n"
            f"Motivo: {reserva.motivo}\n\n"
            f"Atenciosamente,\n"
            f"Sistema de Reserva de Salas"
        )

        html = f"""
        <html>
            <body>
                <h2>Nova reserva recorrente criada</h2>
                <p>Olá {usuario.nome},</p>
                <p>Sua reserva recorrente foi criada com sucesso!</p>
                <h3>Detalhes da reserva:</h3>
                <ul>
                    <li><strong>Sala:</strong> {reserva.sala.identificacao_sala}</li>
                    <li><strong>Bloco:</strong> {reserva.sala.bloco.nome}</li>
                    <li><strong>Período:</strong> {self._format_date(reserva.data_inicio)} a {self._format_date(reserva.data_fim)}</li>
                    <li><strong>Horário:</strong> {reserva.hora_inicio.strftime("%H:%M")} - {reserva.hora_fim.strftime("%H:%M")}</li>
                    <li><strong>Frequência:</strong> {reserva.frequencia.value}</li>
                    <li><strong>Motivo:</strong> {reserva.motivo}</li>
                </ul>
                <p>Atenciosamente,<br>Sistema de Reserva de Salas</p>
            </body>
        </html>
        """

        self.email_client.send_email(
            to_email=usuario.email,
            subject=subject,
            text=text,
            html=html,
            template_data=template_data,
        )
