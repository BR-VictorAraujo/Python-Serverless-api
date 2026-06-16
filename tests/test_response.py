import json
import pytest
from src.utils.response import success, error


class TestSuccess:
    def test_retorna_status_code_correto(self):
        resultado = success(200, {"mensagem": "ok"})
        assert resultado["statusCode"] == 200

    def test_retorna_body_em_json(self):
        dados = {"id": "123", "nome": "Victor"}
        resultado = success(200, dados)
        body = json.loads(resultado["body"])
        assert body["id"] == "123"
        assert body["nome"] == "Victor"

    def test_retorna_header_content_type(self):
        resultado = success(200, {})
        assert resultado["headers"]["Content-Type"] == "application/json"

    def test_retorna_header_cors(self):
        resultado = success(200, {})
        assert resultado["headers"]["Access-Control-Allow-Origin"] == "*"

    def test_status_201_para_criacao(self):
        resultado = success(201, {"id": "abc"})
        assert resultado["statusCode"] == 201


class TestError:
    def test_retorna_status_code_de_erro(self):
        resultado = error(404, "Não encontrado")
        assert resultado["statusCode"] == 404

    def test_retorna_mensagem_de_erro(self):
        resultado = error(400, "Campo obrigatório")
        body = json.loads(resultado["body"])
        assert body["erro"] == "Campo obrigatório"

    def test_retorna_500_para_erro_interno(self):
        resultado = error(500, "Erro interno")
        assert resultado["statusCode"] == 500

    def test_retorna_header_content_type(self):
        resultado = error(400, "Erro")
        assert resultado["headers"]["Content-Type"] == "application/json"