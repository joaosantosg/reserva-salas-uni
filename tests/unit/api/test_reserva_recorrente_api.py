import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.schema.reserva_schema import ReservaRecorrenteCreate, ReservaRecorrenteUpdate
from app.core.commons.exceptions import NotFoundException, BusinessException

client = TestClient(app)

class TestReservaRecorrenteApi:
    """Testes unitários para a API de reservas recorrentes"""
    
    @pytest.fixture
    def auth_headers(self, usuario):
        """Fixture para gerar headers de autenticação"""
        return {
            "Authorization": f"Bearer {usuario.token}",
            "Content-Type": "application/json"
        }

    def test_create_reserva_recorrente_success(self, auth_headers, sala):
        """Testa a criação bem-sucedida de uma reserva recorrente"""
        reserva_data = {
            "sala_id": str(sala.id),
            "inicio": (datetime.now() + timedelta(days=1)).isoformat(),
            "fim": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            "motivo": "Teste",
            "frequencia": "DIARIA",
            "dia_da_semana": None,
            "data_fim": (datetime.now() + timedelta(days=30)).isoformat(),
            "semestre": 1,
            "ano": 2025
        }
        
        response = client.post("/api/v1/reservas-recorrentes", json=reserva_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["sala_id"] == str(sala.id)
        assert data["motivo"] == "Teste"
        assert data["frequencia"] == "DIARIA"
        assert data["ativo"] is True
        assert data["semestre"] == 1
        assert data["ano"] == 2025

    def test_create_reserva_recorrente_unauthorized(self, sala):
        """Testa a criação de reserva recorrente sem autenticação"""
        reserva_data = {
            "sala_id": str(sala.id),
            "inicio": (datetime.now() + timedelta(days=1)).isoformat(),
            "fim": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            "motivo": "Teste",
            "frequencia": "DIARIA",
            "dia_da_semana": None,
            "data_fim": (datetime.now() + timedelta(days=30)).isoformat(),
            "semestre": 1,
            "ano": 2025
        }
        
        response = client.post("/api/v1/reservas-recorrentes", json=reserva_data)
        
        assert response.status_code == 401

    def test_create_reserva_recorrente_sala_not_found(self, auth_headers):
        """Testa a criação de reserva recorrente com sala inexistente"""
        reserva_data = {
            "sala_id": str(uuid4()),
            "inicio": (datetime.now() + timedelta(days=1)).isoformat(),
            "fim": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            "motivo": "Teste",
            "frequencia": "DIARIA",
            "dia_da_semana": None,
            "data_fim": (datetime.now() + timedelta(days=30)).isoformat(),
            "semestre": 1,
            "ano": 2025
        }
        
        response = client.post("/api/v1/reservas-recorrentes", json=reserva_data, headers=auth_headers)
        
        assert response.status_code == 404

    def test_create_reserva_recorrente_past_date(self, auth_headers, sala):
        """Testa a criação de reserva recorrente com data no passado"""
        reserva_data = {
            "sala_id": str(sala.id),
            "inicio": (datetime.now() - timedelta(days=1)).isoformat(),
            "fim": datetime.now().isoformat(),
            "motivo": "Teste",
            "frequencia": "DIARIA",
            "dia_da_semana": None,
            "data_fim": (datetime.now() + timedelta(days=30)).isoformat(),
            "semestre": 1,
            "ano": 2025
        }
        
        response = client.post("/api/v1/reservas-recorrentes", json=reserva_data, headers=auth_headers)
        
        assert response.status_code == 400

    def test_get_reserva_recorrente_success(self, auth_headers, reserva_recorrente):
        """Testa a busca bem-sucedida de uma reserva recorrente"""
        response = client.get(f"/api/v1/reservas-recorrentes/{reserva_recorrente.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(reserva_recorrente.id)
        assert data["sala_id"] == str(reserva_recorrente.sala_id)
        assert data["motivo"] == reserva_recorrente.motivo
        assert data["frequencia"] == reserva_recorrente.frequencia

    def test_get_reserva_recorrente_not_found(self, auth_headers):
        """Testa a busca de reserva recorrente inexistente"""
        response = client.get(f"/api/v1/reservas-recorrentes/{uuid4()}", headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_reserva_recorrente_success(self, auth_headers, reserva_recorrente):
        """Testa a atualização bem-sucedida de uma reserva recorrente"""
        update_data = {
            "motivo": "Novo motivo"
        }
        
        response = client.put(f"/api/v1/reservas-recorrentes/{reserva_recorrente.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["motivo"] == "Novo motivo"
        assert data["id"] == str(reserva_recorrente.id)

    def test_update_reserva_recorrente_not_found(self, auth_headers):
        """Testa a atualização de reserva recorrente inexistente"""
        update_data = {
            "motivo": "Novo motivo"
        }
        
        response = client.put(f"/api/v1/reservas-recorrentes/{uuid4()}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_reserva_recorrente_unauthorized(self, auth_headers, reserva_recorrente):
        """Testa a atualização de reserva recorrente por usuário não autorizado"""
        update_data = {
            "motivo": "Novo motivo"
        }
        
        # Criar um novo usuário e gerar token
        new_user = {
            "email": "test2@example.com",
            "senha": "test123"
        }
        client.post("/api/v1/auth/register", json=new_user)
        login_response = client.post("/api/v1/auth/login", json=new_user)
        new_token = login_response.json()["access_token"]
        new_headers = {
            "Authorization": f"Bearer {new_token}",
            "Content-Type": "application/json"
        }
        
        response = client.put(f"/api/v1/reservas-recorrentes/{reserva_recorrente.id}", json=update_data, headers=new_headers)
        
        assert response.status_code == 403

    def test_delete_reserva_recorrente_success(self, auth_headers, reserva_recorrente):
        """Testa a exclusão bem-sucedida de uma reserva recorrente"""
        response = client.delete(f"/api/v1/reservas-recorrentes/{reserva_recorrente.id}", headers=auth_headers)
        
        assert response.status_code == 204

    def test_delete_reserva_recorrente_not_found(self, auth_headers):
        """Testa a exclusão de reserva recorrente inexistente"""
        response = client.delete(f"/api/v1/reservas-recorrentes/{uuid4()}", headers=auth_headers)
        
        assert response.status_code == 404

    def test_delete_reserva_recorrente_unauthorized(self, auth_headers, reserva_recorrente):
        """Testa a exclusão de reserva recorrente por usuário não autorizado"""
        # Criar um novo usuário e gerar token
        new_user = {
            "email": "test2@example.com",
            "senha": "test123"
        }
        client.post("/api/v1/auth/register", json=new_user)
        login_response = client.post("/api/v1/auth/login", json=new_user)
        new_token = login_response.json()["access_token"]
        new_headers = {
            "Authorization": f"Bearer {new_token}",
            "Content-Type": "application/json"
        }
        
        response = client.delete(f"/api/v1/reservas-recorrentes/{reserva_recorrente.id}", headers=new_headers)
        
        assert response.status_code == 403

    def test_list_reservas_recorrentes(self, auth_headers, reserva_recorrente):
        """Testa a listagem de reservas recorrentes"""
        response = client.get("/api/v1/reservas-recorrentes", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        assert data["paginacao"]["total"] > 0
        assert data["paginacao"]["pagina"] == 1
        assert data["paginacao"]["tamanho"] == 10

    def test_list_reservas_recorrentes_with_filters(self, auth_headers, reserva_recorrente):
        """Testa a listagem de reservas recorrentes com filtros"""
        response = client.get(
            f"/api/v1/reservas-recorrentes?sala_id={reserva_recorrente.sala_id}&usuario_id={reserva_recorrente.usuario_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        assert data["items"][0]["sala_id"] == str(reserva_recorrente.sala_id)
        assert data["items"][0]["usuario_id"] == str(reserva_recorrente.usuario_id)

    def test_recriar_reservas_success(self, auth_headers, reserva_recorrente):
        """Testa a recriação bem-sucedida das reservas individuais"""
        response = client.post(
            f"/api/v1/reservas-recorrentes/{reserva_recorrente.id}/recriar",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Reservas recriadas com sucesso"
        assert data["reservas_criadas"] > 0

    def test_recriar_reservas_not_found(self, auth_headers):
        """Testa a recriação de reservas de uma reserva recorrente inexistente"""
        response = client.post(
            f"/api/v1/reservas-recorrentes/{uuid4()}/recriar",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_recriar_reservas_unauthorized(self, auth_headers, reserva_recorrente):
        """Testa a recriação de reservas por usuário não autorizado"""
        # Criar um novo usuário e gerar token
        new_user = {
            "email": "test2@example.com",
            "senha": "test123"
        }
        client.post("/api/v1/auth/register", json=new_user)
        login_response = client.post("/api/v1/auth/login", json=new_user)
        new_token = login_response.json()["access_token"]
        new_headers = {
            "Authorization": f"Bearer {new_token}",
            "Content-Type": "application/json"
        }
        
        response = client.post(
            f"/api/v1/reservas-recorrentes/{reserva_recorrente.id}/recriar",
            headers=new_headers
        )
        
        assert response.status_code == 403 