import requests
from typing import Dict, Any
from app.core.config.settings import settings


class EmailClient:
    """Cliente para envio de emails usando Mailgun API"""

    def __init__(self):
        self.api_key = settings.MAILGUN_API_KEY
        self.domain = settings.MAILGUN_DOMAIN
        self.base_url = f"https://api.mailgun.net/v3/{self.domain}/messages"

        if not self.api_key or not self.domain:
            raise ValueError(
                "MAILGUN_API_KEY e MAILGUN_DOMAIN devem estar configurados nas variáveis de ambiente"
            )

    def send_email(
        self,
        to_email: str,
        subject: str,
        text: str,
        html: str = None,
        template_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Envia um email usando a API do Mailgun.

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            text: Conteúdo em texto plano
            html: Conteúdo em HTML (opcional)
            template_data: Dados para substituição no template (opcional)

        Returns:
            Dict com a resposta da API
        """
        data = {
            "from": f"Reserva de Salas <noreply@{self.domain}>",
            "to": to_email,
            "subject": subject,
            "text": text,
            "html": html,
        }

        if template_data:
            data["h:X-Mailgun-Variables"] = str(template_data)

        response = requests.post(self.base_url, auth=("api", self.api_key), data=data)

        if response.status_code != 200:
            raise Exception(f"Erro ao enviar email: {response.text}")

        return response.json()

    def send_batch_emails(
        self,
        recipients: Dict[str, Dict[str, str]],
        subject_template: str,
        text_template: str,
        html_template: str = None,
    ) -> Dict[str, Any]:
        """
        Envia emails em lote usando a API do Mailgun.

        Args:
            recipients: Dicionário com emails e dados dos destinatários
            subject_template: Template do assunto com variáveis %recipient.variavel%
            text_template: Template do texto com variáveis %recipient.variavel%
            html_template: Template HTML com variáveis %recipient.variavel% (opcional)

        Returns:
            Dict com a resposta da API
        """
        data = {
            "from": f"Reserva de Salas <noreply@{self.domain}>",
            "to": list(recipients.keys()),
            "subject": subject_template,
            "text": text_template,
            "html": html_template,
            "recipient-variables": str(recipients),
        }

        response = requests.post(self.base_url, auth=("api", self.api_key), data=data)

        if response.status_code != 200:
            raise Exception(f"Erro ao enviar emails em lote: {response.text}")

        return response.json()
