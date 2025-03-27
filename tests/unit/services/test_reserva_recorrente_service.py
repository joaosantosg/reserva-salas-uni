import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.services.reserva_recorrente_service import ReservaRecorrenteService
from app.schema.reserva_schema import ReservaRecorrenteCreate, ReservaRecorrenteUpdate
from app.core.commons.exceptions import NotFoundException, BusinessException

class TestReservaRecorrenteService:
    """Testes unitários para o serviço de reservas recorrentes"""
    
    @pytest.fixture
    def service(self, reserva_recorrente_repository, sala_repository, usuario_repository, reserva_repository, email_service):
        return ReservaRecorrenteService(
            reserva_recorrente_repository=reserva_recorrente_repository,
            sala_repository=sala_repository,
            usuario_repository=usuario_repository,
            reserva_repository=reserva_repository,
            email_service=email_service
        )

    def test_create_reserva_recorrente_success(self, service, sala, usuario):
        """Testa a criação bem-sucedida de uma reserva recorrente"""
        reserva_data = ReservaRecorrenteCreate(
            sala_id=sala.id,
            inicio=datetime.now() + timedelta(days=1),
            fim=datetime.now() + timedelta(days=1, hours=2),
            motivo="Teste",
            frequencia="DIARIA",
            dia_da_semana=None,
            data_fim=datetime.now() + timedelta(days=30),
            semestre=1,
            ano=2025
        )
        
        reserva = service.create(reserva_data, usuario.id)
        
        assert reserva.sala_id == sala.id
        assert reserva.usuario_id == usuario.id
        assert reserva.motivo == "Teste"
        assert reserva.frequencia == "DIARIA"
        assert reserva.ativo is True
        assert reserva.semestre == 1
        assert reserva.ano == 2025

    def test_create_reserva_recorrente_sala_not_found(self, service, usuario):
        """Testa a criação de reserva recorrente com sala inexistente"""
        reserva_data = ReservaRecorrenteCreate(
            sala_id=uuid4(),
            inicio=datetime.now() + timedelta(days=1),
            fim=datetime.now() + timedelta(days=1, hours=2),
            motivo="Teste",
            frequencia="DIARIA",
            dia_da_semana=None,
            data_fim=datetime.now() + timedelta(days=30),
            semestre=1,
            ano=2025
        )
        
        with pytest.raises(NotFoundException):
            service.create(reserva_data, usuario.id)

    def test_create_reserva_recorrente_usuario_not_found(self, service, sala):
        """Testa a criação de reserva recorrente com usuário inexistente"""
        reserva_data = ReservaRecorrenteCreate(
            sala_id=sala.id,
            inicio=datetime.now() + timedelta(days=1),
            fim=datetime.now() + timedelta(days=1, hours=2),
            motivo="Teste",
            frequencia="DIARIA",
            dia_da_semana=None,
            data_fim=datetime.now() + timedelta(days=30),
            semestre=1,
            ano=2025
        )
        
        with pytest.raises(NotFoundException):
            service.create(reserva_data, uuid4())

    def test_create_reserva_recorrente_past_date(self, service, sala, usuario):
        """Testa a criação de reserva recorrente com data no passado"""
        reserva_data = ReservaRecorrenteCreate(
            sala_id=sala.id,
            inicio=datetime.now() - timedelta(days=1),
            fim=datetime.now(),
            motivo="Teste",
            frequencia="DIARIA",
            dia_da_semana=None,
            data_fim=datetime.now() + timedelta(days=30),
            semestre=1,
            ano=2025
        )
        
        with pytest.raises(BusinessException):
            service.create(reserva_data, usuario.id)

    def test_create_reserva_recorrente_conflict(self, service, sala, usuario, reserva_recorrente):
        """Testa a criação de reserva recorrente com conflito de horário"""
        reserva_data = ReservaRecorrenteCreate(
            sala_id=sala.id,
            inicio=reserva_recorrente.inicio,
            fim=reserva_recorrente.fim,
            motivo="Teste",
            frequencia="DIARIA",
            dia_da_semana=None,
            data_fim=datetime.now() + timedelta(days=30),
            semestre=1,
            ano=2025
        )
        
        with pytest.raises(BusinessException):
            service.create(reserva_data, usuario.id)

    def test_update_reserva_recorrente_success(self, service, reserva_recorrente):
        """Testa a atualização bem-sucedida de uma reserva recorrente"""
        update_data = ReservaRecorrenteUpdate(
            motivo="Novo motivo"
        )
        
        updated = service.update(reserva_recorrente.id, update_data, reserva_recorrente.usuario_id)
        
        assert updated.motivo == "Novo motivo"
        assert updated.sala_id == reserva_recorrente.sala_id
        assert updated.usuario_id == reserva_recorrente.usuario_id

    def test_update_reserva_recorrente_not_found(self, service):
        """Testa a atualização de reserva recorrente inexistente"""
        update_data = ReservaRecorrenteUpdate(
            motivo="Novo motivo"
        )
        
        with pytest.raises(NotFoundException):
            service.update(uuid4(), update_data, uuid4())

    def test_update_reserva_recorrente_unauthorized(self, service, reserva_recorrente):
        """Testa a atualização de reserva recorrente por usuário não autorizado"""
        update_data = ReservaRecorrenteUpdate(
            motivo="Novo motivo"
        )
        
        with pytest.raises(BusinessException):
            service.update(reserva_recorrente.id, update_data, uuid4())

    def test_delete_reserva_recorrente_success(self, service, reserva_recorrente):
        """Testa a exclusão bem-sucedida de uma reserva recorrente"""
        service.delete(reserva_recorrente.id, reserva_recorrente.usuario_id)
        
        with pytest.raises(NotFoundException):
            service.get_by_id(reserva_recorrente.id)

    def test_delete_reserva_recorrente_not_found(self, service):
        """Testa a exclusão de reserva recorrente inexistente"""
        with pytest.raises(NotFoundException):
            service.delete(uuid4(), uuid4())

    def test_delete_reserva_recorrente_unauthorized(self, service, reserva_recorrente):
        """Testa a exclusão de reserva recorrente por usuário não autorizado"""
        with pytest.raises(BusinessException):
            service.delete(reserva_recorrente.id, uuid4())

    def test_get_by_id_success(self, service, reserva_recorrente):
        """Testa a busca de reserva recorrente por ID"""
        result = service.get_by_id(reserva_recorrente.id)
        
        assert result.id == reserva_recorrente.id
        assert result.sala_id == reserva_recorrente.sala_id
        assert result.usuario_id == reserva_recorrente.usuario_id

    def test_get_by_id_not_found(self, service):
        """Testa a busca de reserva recorrente inexistente"""
        with pytest.raises(NotFoundException):
            service.get_by_id(uuid4())

    def test_get_by_query(self, service, reserva_recorrente):
        """Testa a busca de reservas recorrentes com filtros"""
        result = service.get_by_query(
            sala_id=reserva_recorrente.sala_id,
            usuario_id=reserva_recorrente.usuario_id,
            pagina=1,
            tamanho=10
        )
        
        assert len(result.items) > 0
        assert result.items[0].id == reserva_recorrente.id
        assert result.paginacao.total > 0
        assert result.paginacao.pagina == 1
        assert result.paginacao.tamanho == 10

    def test_recriar_reservas_success(self, service, reserva_recorrente):
        """Testa a recriação bem-sucedida das reservas individuais"""
        result = service.recriar_reservas(reserva_recorrente.id, reserva_recorrente.usuario_id)
        
        assert result["message"] == "Reservas recriadas com sucesso"
        assert result["reservas_criadas"] > 0

    def test_recriar_reservas_not_found(self, service):
        """Testa a recriação de reservas de uma reserva recorrente inexistente"""
        with pytest.raises(NotFoundException):
            service.recriar_reservas(uuid4(), uuid4())

    def test_recriar_reservas_unauthorized(self, service, reserva_recorrente):
        """Testa a recriação de reservas por usuário não autorizado"""
        with pytest.raises(BusinessException):
            service.recriar_reservas(reserva_recorrente.id, uuid4()) 