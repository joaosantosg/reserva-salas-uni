import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.repository.reserva_repository import ReservaRepository
from app.model.reserva_model import Reserva

class TestReservaRepository:
    """Testes unitários para o repositório de reservas"""
    
    @pytest.fixture
    def repository(self, db_session):
        return ReservaRepository(db_session)

    def test_create_reserva(self, repository, sala, usuario):
        """Testa a criação de uma reserva"""
        reserva = Reserva(
            sala_id=sala.id,
            usuario_id=usuario.id,
            inicio=datetime.now() + timedelta(days=1),
            fim=datetime.now() + timedelta(days=1, hours=2),
            motivo="Teste"
        )
        
        created = repository.create(reserva)
        
        assert created.id is not None
        assert created.sala_id == sala.id
        assert created.usuario_id == usuario.id
        assert created.motivo == "Teste"
        assert created.ativo is True

    def test_get_by_id(self, repository, reserva):
        """Testa a busca de reserva por ID"""
        result = repository.get_by_id(reserva.id)
        
        assert result.id == reserva.id
        assert result.sala_id == reserva.sala_id
        assert result.usuario_id == reserva.usuario_id

    def test_get_by_id_not_found(self, repository):
        """Testa a busca de reserva inexistente"""
        result = repository.get_by_id(uuid4())
        assert result is None

    def test_get_by_query(self, repository, reserva):
        """Testa a busca de reservas com filtros"""
        result = repository.get_by_query(
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

    def test_get_by_period(self, repository, reserva):
        """Testa a busca de reservas por período"""
        result = repository.get_by_period(
            sala_id=reserva.sala_id,
            data_inicio=reserva.inicio.date(),
            data_fim=reserva.fim.date()
        )
        
        assert len(result) > 0
        assert result[0].id == reserva.id

    def test_get_by_sala_and_date(self, repository, reserva):
        """Testa a busca de reservas por sala e data"""
        result = repository.get_by_sala_and_date(
            sala_id=reserva.sala_id,
            data=reserva.inicio.date()
        )
        
        assert len(result) > 0
        assert result[0].id == reserva.id

    def test_update(self, repository, reserva):
        """Testa a atualização de uma reserva"""
        reserva.motivo = "Novo motivo"
        updated = repository.update(reserva)
        
        assert updated.motivo == "Novo motivo"
        assert updated.id == reserva.id

    def test_soft_delete(self, repository, reserva):
        """Testa a exclusão lógica de uma reserva"""
        repository.soft_delete(reserva.id, reserva.usuario_id)
        
        deleted = repository.get_by_id(reserva.id)
        assert deleted.ativo is False
        assert deleted.excluido_em is not None
        assert deleted.excluido_por == reserva.usuario_id

    def test_soft_delete_reservas_recorrentes(self, repository, reserva_recorrente):
        """Testa a exclusão lógica de reservas de uma reserva recorrente"""
        repository.soft_delete_reservas_recorrentes(reserva_recorrente.id)
        
        result = repository.get_by_query(
            reserva_recorrente_id=reserva_recorrente.id,
            pagina=1,
            tamanho=10
        )
        
        for reserva in result.items:
            assert reserva.ativo is False
            assert reserva.excluido_em is not None
            assert reserva.excluido_por == reserva_recorrente.usuario_id 