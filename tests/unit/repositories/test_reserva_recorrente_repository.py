import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.repository.reserva_recorrente_repository import ReservaRecorrenteRepository
from app.model.reserva_recorrente_model import ReservaRecorrente

class TestReservaRecorrenteRepository:
    """Testes unitários para o repositório de reservas recorrentes"""
    
    @pytest.fixture
    def repository(self, db_session):
        return ReservaRecorrenteRepository(db_session)

    def test_create_reserva_recorrente(self, repository, sala, usuario):
        """Testa a criação de uma reserva recorrente"""
        reserva = ReservaRecorrente(
            sala_id=sala.id,
            usuario_id=usuario.id,
            inicio=datetime.now() + timedelta(days=1),
            fim=datetime.now() + timedelta(days=1, hours=2),
            motivo="Teste",
            frequencia="DIARIA",
            dia_da_semana=None,
            data_fim=datetime.now() + timedelta(days=30),
            semestre=1,
            ano=2025
        )
        
        created = repository.create(reserva)
        
        assert created.id is not None
        assert created.sala_id == sala.id
        assert created.usuario_id == usuario.id
        assert created.motivo == "Teste"
        assert created.frequencia == "DIARIA"
        assert created.semestre == 1
        assert created.ano == 2025

    def test_get_by_id(self, repository, reserva_recorrente):
        """Testa a busca de reserva recorrente por ID"""
        result = repository.get_by_id(reserva_recorrente.id)
        
        assert result.id == reserva_recorrente.id
        assert result.sala_id == reserva_recorrente.sala_id
        assert result.usuario_id == reserva_recorrente.usuario_id

    def test_get_by_id_not_found(self, repository):
        """Testa a busca de reserva recorrente inexistente"""
        result = repository.get_by_id(uuid4())
        assert result is None

    def test_get_by_query(self, repository, reserva_recorrente):
        """Testa a busca de reservas recorrentes com filtros"""
        result = repository.get_by_query(
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

    def test_get_by_period(self, repository, reserva_recorrente):
        """Testa a busca de reservas recorrentes por período"""
        result = repository.get_by_period(
            sala_id=reserva_recorrente.sala_id,
            data_inicio=reserva_recorrente.inicio.date(),
            data_fim=reserva_recorrente.data_fim.date()
        )
        
        assert len(result) > 0
        assert result[0].id == reserva_recorrente.id

    def test_check_conflict(self, repository, reserva_recorrente):
        """Testa a verificação de conflito de horário"""
        has_conflict = repository.check_conflict(
            sala_id=reserva_recorrente.sala_id,
            inicio=reserva_recorrente.inicio,
            fim=reserva_recorrente.fim,
            exclude_id=reserva_recorrente.id
        )
        
        assert has_conflict is False

    def test_check_conflict_with_conflict(self, repository, reserva_recorrente):
        """Testa a verificação de conflito de horário com conflito"""
        has_conflict = repository.check_conflict(
            sala_id=reserva_recorrente.sala_id,
            inicio=reserva_recorrente.inicio,
            fim=reserva_recorrente.fim,
            exclude_id=None
        )
        
        assert has_conflict is True

    def test_update(self, repository, reserva_recorrente):
        """Testa a atualização de uma reserva recorrente"""
        reserva_recorrente.motivo = "Novo motivo"
        updated = repository.update(reserva_recorrente)
        
        assert updated.motivo == "Novo motivo"
        assert updated.id == reserva_recorrente.id

    def test_soft_delete(self, repository, reserva_recorrente):
        """Testa a exclusão lógica de uma reserva recorrente"""
        repository.soft_delete(reserva_recorrente.id, reserva_recorrente.usuario_id)
        
        deleted = repository.get_by_id(reserva_recorrente.id)
        assert deleted.excluido_em is not None
        assert deleted.excluido_por == reserva_recorrente.usuario_id

    def test_get_by_semestre_and_ano(self, repository, reserva_recorrente):
        """Testa a busca de reservas recorrentes por semestre e ano"""
        result = repository.get_by_semestre_and_ano(
            semestre=reserva_recorrente.semestre,
            ano=reserva_recorrente.ano
        )
        
        assert len(result) > 0
        assert result[0].id == reserva_recorrente.id
        assert result[0].semestre == reserva_recorrente.semestre
        assert result[0].ano == reserva_recorrente.ano 