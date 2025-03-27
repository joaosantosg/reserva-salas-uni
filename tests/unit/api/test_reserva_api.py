import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.schema.reserva_schema import ReservaCreate, ReservaUpdate
from app.core.commons.exceptions import NotFoundException, BusinessException

client = TestClient(app)

class TestReservaApi:
    """Testes unitários para a API de reservas"""
    
    @pytest.fixture
    def auth_headers(self, usuario):
        """Fixture para gerar headers de autenticação"""
        return {
            "Authorization": f"Bearer {usuario.token}",
            "Content-Type": "application/json"
        }

    def test_create_reserva_success(self, auth_headers, sala):
        """Testa a criação bem-sucedida de uma reserva"""
        reserva_data = {
            "sala_id": str(sala.id),
            "inicio": (datetime.now() + timedelta(days=1)).isoformat(),
            "fim": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            "motivo": "Teste"
        }
        
        response = client.post("/api/v1/reservas", json=reserva_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["sala_id"] == str(sala.id)
        assert data["motivo"] == "Teste"
        assert data["ativo"] is True

    def test_create_reserva_unauthorized(self, sala):
        """Testa a criação de reserva sem autenticação"""
        reserva_data = {
            "sala_id": str(sala.id),
            "inicio": (datetime.now() + timedelta(days=1)).isoformat(),
            "fim": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            "motivo": "Teste"
        }
        
        response = client.post("/api/v1/reservas", json=reserva_data)
        
        assert response.status_code == 401

    def test_create_reserva_sala_not_found(self, auth_headers):
        """Testa a criação de reserva com sala inexistente"""
        reserva_data = {
            "sala_id": str(uuid4()),
            "inicio": (datetime.now() + timedelta(days=1)).isoformat(),
            "fim": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            "motivo": "Teste"
        }
        
        response = client.post("/api/v1/reservas", json=reserva_data, headers=auth_headers)
        
        assert response.status_code == 404

    def test_create_reserva_past_date(self, auth_headers, sala):
        """Testa a criação de reserva com data no passado"""
        reserva_data = {
            "sala_id": str(sala.id),
            "inicio": (datetime.now() - timedelta(days=1)).isoformat(),
            "fim": datetime.now().isoformat(),
            "motivo": "Teste"
        }
        
        response = client.post("/api/v1/reservas", json=reserva_data, headers=auth_headers)
        
        assert response.status_code == 400

    def test_get_reserva_success(self, auth_headers, reserva):
        """Testa a busca bem-sucedida de uma reserva"""
        response = client.get(f"/api/v1/reservas/{reserva.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(reserva.id)
        assert data["sala_id"] == str(reserva.sala_id)
        assert data["motivo"] == reserva.motivo

    def test_get_reserva_not_found(self, auth_headers):
        """Testa a busca de reserva inexistente"""
        response = client.get(f"/api/v1/reservas/{uuid4()}", headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_reserva_success(self, auth_headers, reserva):
        """Testa a atualização bem-sucedida de uma reserva"""
        update_data = {
            "motivo": "Novo motivo"
        }
        
        response = client.put(f"/api/v1/reservas/{reserva.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["motivo"] == "Novo motivo"
        assert data["id"] == str(reserva.id)

    def test_update_reserva_not_found(self, auth_headers):
        """Testa a atualização de reserva inexistente"""
        update_data = {
            "motivo": "Novo motivo"
        }
        
        response = client.put(f"/api/v1/reservas/{uuid4()}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_reserva_unauthorized(self, auth_headers, reserva):
        """Testa a atualização de reserva por usuário não autorizado"""
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
        
        response = client.put(f"/api/v1/reservas/{reserva.id}", json=update_data, headers=new_headers)
        
        assert response.status_code == 403

    def test_delete_reserva_success(self, auth_headers, reserva):
        """Testa a exclusão bem-sucedida de uma reserva"""
        response = client.delete(f"/api/v1/reservas/{reserva.id}", headers=auth_headers)
        
        assert response.status_code == 204

    def test_delete_reserva_not_found(self, auth_headers):
        """Testa a exclusão de reserva inexistente"""
        response = client.delete(f"/api/v1/reservas/{uuid4()}", headers=auth_headers)
        
        assert response.status_code == 404

    def test_delete_reserva_unauthorized(self, auth_headers, reserva):
        """Testa a exclusão de reserva por usuário não autorizado"""
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
        
        response = client.delete(f"/api/v1/reservas/{reserva.id}", headers=new_headers)
        
        assert response.status_code == 403

    def test_list_reservas(self, auth_headers, reserva):
        """Testa a listagem de reservas"""
        response = client.get("/api/v1/reservas", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        assert data["paginacao"]["total"] > 0
        assert data["paginacao"]["pagina"] == 1
        assert data["paginacao"]["tamanho"] == 10

    def test_list_reservas_with_filters(self, auth_headers, reserva):
        """Testa a listagem de reservas com filtros"""
        response = client.get(
            f"/api/v1/reservas?sala_id={reserva.sala_id}&usuario_id={reserva.usuario_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        assert data["items"][0]["sala_id"] == str(reserva.sala_id)
        assert data["items"][0]["usuario_id"] == str(reserva.usuario_id) 