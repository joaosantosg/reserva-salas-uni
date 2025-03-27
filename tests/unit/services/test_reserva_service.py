import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.services.reserva_service import ReservaService
from app.schema.reserva_schema import ReservaCreate, ReservaUpdate
from app.core.commons.exceptions import NotFoundException, BusinessException

class TestReservaService:
    """Testes unitários para o serviço de reservas"""
    
    @pytest.fixture
    def service(self, reserva_repository, sala_repository, usuario_repository, email_service):
        return ReservaService(
            reserva_repository=reserva_repository,
            sala_repository=sala_repository,
            usuario_repository=usuario_repository,
            email_service=email_service
        )

    def test_create_reserva_success(self, service, sala, usuario):
        """Testa a criação bem-sucedida de uma reserva"""
        reserva_data = ReservaCreate(
            sala_id=sala.id,
            inicio=datetime.now() + timedelta(days=1),
            fim=datetime.now() + timedelta(days=1, hours=2),
            motivo="Teste"
        )
        
        reserva = service.create(reserva_data, usuario.id)
        
        assert reserva.sala_id == sala.id
        assert reserva.usuario_id == usuario.id
        assert reserva.motivo == "Teste"
        assert reserva.ativo is True

    def test_create_reserva_sala_not_found(self, service, usuario):
        """Testa a criação de reserva com sala inexistente"""
        reserva_data = ReservaCreate(
            sala_id=uuid4(),
            inicio=datetime.now() + timedelta(days=1),
            fim=datetime.now() + timedelta(days=1, hours=2),
            motivo="Teste"
        )
        
        with pytest.raises(NotFoundException):
            service.create(reserva_data, usuario.id)

    def test_create_reserva_usuario_not_found(self, service, sala):
        """Testa a criação de reserva com usuário inexistente"""
        reserva_data = ReservaCreate(
            sala_id=sala.id,
            inicio=datetime.now() + timedelta(days=1),
            fim=datetime.now() + timedelta(days=1, hours=2),
            motivo="Teste"
        )
        
        with pytest.raises(NotFoundException):
            service.create(reserva_data, uuid4())

    def test_create_reserva_past_date(self, service, sala, usuario):
        """Testa a criação de reserva com data no passado"""
        reserva_data = ReservaCreate(
            sala_id=sala.id,
            inicio=datetime.now() - timedelta(days=1),
            fim=datetime.now(),
            motivo="Teste"
        )
        
        with pytest.raises(BusinessException):
            service.create(reserva_data, usuario.id)

    def test_create_reserva_conflict(self, service, sala, usuario, reserva):
        """Testa a criação de reserva com conflito de horário"""
        reserva_data = ReservaCreate(
            sala_id=sala.id,
            inicio=reserva.inicio,
            fim=reserva.fim,
            motivo="Teste"
        )
        
        with pytest.raises(BusinessException):
            service.create(reserva_data, usuario.id)

    def test_update_reserva_success(self, service, reserva):
        """Testa a atualização bem-sucedida de uma reserva"""
        update_data = ReservaUpdate(
            motivo="Novo motivo"
        )
        
        updated = service.update(reserva.id, update_data, reserva.usuario_id)
        
        assert updated.motivo == "Novo motivo"
        assert updated.sala_id == reserva.sala_id
        assert updated.usuario_id == reserva.usuario_id

    def test_update_reserva_not_found(self, service):
        """Testa a atualização de reserva inexistente"""
        update_data = ReservaUpdate(
            motivo="Novo motivo"
        )
        
        with pytest.raises(NotFoundException):
            service.update(uuid4(), update_data, uuid4())

    def test_update_reserva_unauthorized(self, service, reserva):
        """Testa a atualização de reserva por usuário não autorizado"""
        update_data = ReservaUpdate(
            motivo="Novo motivo"
        )
        
        with pytest.raises(BusinessException):
            service.update(reserva.id, update_data, uuid4())

    def test_delete_reserva_success(self, service, reserva):
        """Testa a exclusão bem-sucedida de uma reserva"""
        service.delete(reserva.id, reserva.usuario_id)
        
        with pytest.raises(NotFoundException):
            service.get_by_id(reserva.id)

    def test_delete_reserva_not_found(self, service):
        """Testa a exclusão de reserva inexistente"""
        with pytest.raises(NotFoundException):
            service.delete(uuid4(), uuid4())

    def test_delete_reserva_unauthorized(self, service, reserva):
        """Testa a exclusão de reserva por usuário não autorizado"""
        with pytest.raises(BusinessException):
            service.delete(reserva.id, uuid4())

    def test_get_by_id_success(self, service, reserva):
        """Testa a busca de reserva por ID"""
        result = service.get_by_id(reserva.id)
        
        assert result.id == reserva.id
        assert result.sala_id == reserva.sala_id
        assert result.usuario_id == reserva.usuario_id

    def test_get_by_id_not_found(self, service):
        """Testa a busca de reserva inexistente"""
        with pytest.raises(NotFoundException):
            service.get_by_id(uuid4())

    def test_get_by_query(self, service, reserva):
        """Testa a busca de reservas com filtros"""
        result = service.get_by_query(
            sala_id=reserva.sala_id,
            usuario_id=reserva.usuario_id,
            pagina=1,
            tamanho=10
        )
        
        assert len(result.items) > 0
        assert result.items[0].id == reserva.id
        assert result.paginacao.total > 0
        assert result.paginacao.pagina == 1
        assert result.paginacao.tamanho == 10 