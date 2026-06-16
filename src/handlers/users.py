import json
import uuid
import pg8000.native
import os
from utils.response import success, error


def get_connection():
    """Retorna uma conexão com o banco PostgreSQL via variáveis de ambiente."""
    return pg8000.native.Connection(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=int(os.environ.get("DB_PORT", 5432)),
        ssl_context=True
    )


def lambda_handler(event, context):
    """Ponto de entrada do Lambda. Roteia para a função correta."""
    method = event["httpMethod"]
    path   = event["path"]

    routes = {
        ("GET",    "/users"):      list_users,
        ("POST",   "/users"):      lambda: create_user(event),
        ("GET",    "/users/{id}"): lambda: get_user(event),
        ("PUT",    "/users/{id}"): lambda: update_user(event),
        ("DELETE", "/users/{id}"): lambda: delete_user(event),
    }

    normalized = normalize_path(path)
    handler    = routes.get((method, normalized))

    if not handler:
        return error(404, "Rota não encontrada")

    try:
        return handler()
    except Exception as e:
        return error(500, str(e))


def normalize_path(path):
    """Converte /users/abc123 → /users/{id} para match nas rotas."""
    parts = path.strip("/").split("/")
    if len(parts) == 2 and parts[0] == "users":
        return "/users/{id}"
    return path


def list_users():
    """Retorna todos os usuários ativos."""
    conn  = get_connection()
    rows  = conn.run("SELECT id, nome, email, criado_em FROM usuarios WHERE ativo = true")
    users = [{"id": r[0], "nome": r[1], "email": r[2], "criado_em": str(r[3])} for r in rows]
    conn.close()
    return success(200, users)


def get_user(event):
    """Retorna um usuário pelo ID."""
    user_id = event["pathParameters"]["id"]
    conn    = get_connection()
    rows    = conn.run(
        "SELECT id, nome, email, criado_em FROM usuarios WHERE id = :id AND ativo = true",
        id=user_id
    )
    conn.close()

    if not rows:
        return error(404, "Usuário não encontrado")

    r = rows[0]
    return success(200, {"id": r[0], "nome": r[1], "email": r[2], "criado_em": str(r[3])})


def create_user(event):
    """Cria um novo usuário."""
    body = json.loads(event["body"])

    if not body.get("nome") or not body.get("email"):
        return error(400, "Campos 'nome' e 'email' são obrigatórios")

    new_id = str(uuid.uuid4())
    conn   = get_connection()
    conn.run(
        "INSERT INTO usuarios (id, nome, email) VALUES (:id, :nome, :email)",
        id=new_id, nome=body["nome"], email=body["email"]
    )
    conn.close()
    return success(201, {"id": new_id, "mensagem": "Usuário criado com sucesso"})


def update_user(event):
    """Atualiza nome e email de um usuário existente."""
    user_id = event["pathParameters"]["id"]
    body    = json.loads(event["body"])

    if not body.get("nome") or not body.get("email"):
        return error(400, "Campos 'nome' e 'email' são obrigatórios")

    conn = get_connection()
    conn.run(
        "UPDATE usuarios SET nome = :nome, email = :email WHERE id = :id AND ativo = true",
        nome=body["nome"], email=body["email"], id=user_id
    )
    conn.close()
    return success(200, {"mensagem": "Usuário atualizado com sucesso"})


def delete_user(event):
    """Soft delete — marca o usuário como inativo."""
    user_id = event["pathParameters"]["id"]
    conn    = get_connection()
    conn.run(
        "UPDATE usuarios SET ativo = false WHERE id = :id AND ativo = true",
        id=user_id
    )
    conn.close()
    return success(200, {"mensagem": "Usuário removido com sucesso"})