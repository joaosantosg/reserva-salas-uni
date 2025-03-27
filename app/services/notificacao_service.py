from datetime import datetime
from typing import List
from app.model.reserva_model import Reserva
from app.model.usuario_model import Usuario

class NotificacaoService:
    """Serviço responsável pelo envio de notificações"""
    
    def __init__(self):
        self.log_file = "notificacoes.log"

    def notificar_reservas_futuras(self, reservas: List[Reserva], usuario: Usuario) -> None:
        """
        Simula o envio de notificações para reservas futuras.
        Salva as notificações em um arquivo de log.
        """
        data_atual = datetime.now()
        
        for reserva in reservas:
            if reserva.inicio > data_atual:
                mensagem = (
                    f"[{data_atual.strftime('%d/%m/%Y %H:%M:%S')}] "
                    f"Notificação para {usuario.nome}:\n"
                    f"Você tem uma reserva agendada para:\n"
                    f"Sala: {reserva.sala.numero}\n"
                    f"Data: {reserva.inicio.strftime('%d/%m/%Y')}\n"
                    f"Horário: {reserva.inicio.strftime('%H:%M')} - {reserva.fim.strftime('%H:%M')}\n"
                    f"Motivo: {reserva.motivo}\n"
                    f"{'='*50}\n"
                )
                
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(mensagem) 