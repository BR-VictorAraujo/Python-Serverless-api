import json
import pytest
from unittest.mock import patch, MagicMock
from src.handlers.users import (
    lambda_handler,
    normalize_path,
    list_users,
    get_user,
    create_user,
    update_user,
    delete_user
)


def evento(method, path, body=None, path_params=None):
    """Cria um evento simulado do API Gateway."""
    return {
        "httpMethod": method,
        "path": path,
        "pathParameters": path_params or {},
        "body": json.dumps(body) if body else None
    }


class TestNormalizePath:
    def test_converte_path_com_id(self):
        assert normalize_path("/users/abc123") == "/users/{id}"

    def test_mantem_path_sem_id(self):
        assert normalize_path("/users") == "/users"

    def test_mantem_path_desconhecido(self):
        assert normalize_path("/outro") == "/outro"


class TestLambdaHandler:
    def test_retorna_404_para_rota_inexistente(self):
        ev = evento("GET", "/rota-inexistente")
        resultado = lambda_handler(ev, {})
        assert resultado["statusCode"] == 404

    @patch("src.handlers.users.get_connection")
    def test_lista_usuarios(self, mock_conn):
        mock_cursor = MagicMock()
        mock_cursor.run.return_value = [
            ("id-1", "Victor", "victor@email.com", "2026-01-01")
        ]
        mock_conn.return_value = mock_cursor

        ev = evento("GET", "/users")
        resultado = lambda_handler(ev, {})

        assert resultado["statusCode"] == 200
        body = json.loads(resultado["body"])
        assert len(body) == 1
        assert body[0]["nome"] == "Victor"

    @patch("src.handlers.users.get_connection")
    def test_cria_usuario_com_sucesso(self, mock_conn):
        mock_cursor = MagicMock()
        mock_conn.return_value = mock_cursor

        ev = evento("POST", "/users", body={"nome": "Victor", "email": "victor@email.com"})
        resultado = lambda_handler(ev, {})

        assert resultado["statusCode"] == 201
        body = json.loads(resultado["body"])
        assert "id" in body
        assert body["mensagem"] == "Usuário criado com sucesso"

    @patch("src.handlers.users.get_connection")
    def test_cria_usuario_sem_nome_retorna_400(self, mock_conn):
        ev = evento("POST", "/users", body={"email": "victor@email.com"})
        resultado = lambda_handler(ev, {})
        assert resultado["statusCode"] == 400

    @patch("src.handlers.users.get_connection")
    def test_cria_usuario_sem_email_retorna_400(self, mock_conn):
        ev = evento("POST", "/users", body={"nome": "Victor"})
        resultado = lambda_handler(ev, {})
        assert resultado["statusCode"] == 400

    @patch("src.handlers.users.get_connection")
    def test_busca_usuario_existente(self, mock_conn):
        mock_cursor = MagicMock()
        mock_cursor.run.return_value = [
            ("id-1", "Victor", "victor@email.com", "2026-01-01")
        ]
        mock_conn.return_value = mock_cursor

        ev = evento("GET", "/users/id-1", path_params={"id": "id-1"})
        resultado = lambda_handler(ev, {})

        assert resultado["statusCode"] == 200
        body = json.loads(resultado["body"])
        assert body["nome"] == "Victor"

    @patch("src.handlers.users.get_connection")
    def test_busca_usuario_inexistente_retorna_404(self, mock_conn):
        mock_cursor = MagicMock()
        mock_cursor.run.return_value = []
        mock_conn.return_value = mock_cursor

        ev = evento("GET", "/users/id-inexistente", path_params={"id": "id-inexistente"})
        resultado = lambda_handler(ev, {})

        assert resultado["statusCode"] == 404

    @patch("src.handlers.users.get_connection")
    def test_atualiza_usuario_com_sucesso(self, mock_conn):
        mock_cursor = MagicMock()
        mock_conn.return_value = mock_cursor

        ev = evento(
            "PUT", "/users/id-1",
            body={"nome": "Victor Atualizado", "email": "novo@email.com"},
            path_params={"id": "id-1"}
        )
        resultado = lambda_handler(ev, {})
        assert resultado["statusCode"] == 200

    @patch("src.handlers.users.get_connection")
    def test_deleta_usuario_com_sucesso(self, mock_conn):
        mock_cursor = MagicMock()
        mock_conn.return_value = mock_cursor

        ev = evento("DELETE", "/users/id-1", path_params={"id": "id-1"})
        resultado = lambda_handler(ev, {})
        assert resultado["statusCode"] == 200