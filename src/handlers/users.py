import json
import uuid
import psycopg2
import os
from utils.response import success, error


def get_connection():
    """Retorna uma conexão com o banco PostgreSQL via variáveis de ambiente."""
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=int(os.environ.get("DB_PORT", 5432))
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

    # Normaliza o path para match com as rotas
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
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, criado_em FROM usuarios WHERE ativo = true"
            )
            rows = cur.fetchall()

    users = [
        {"id": r[0], "nome": r[1], "email": r[2], "criado_em": str(r[3])}
        for r in rows
    ]
    return success(200, users)


def get_user(event):
    """Retorna um usuário pelo ID."""
    user_id = event["pathParameters"]["id"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, criado_em FROM usuarios WHERE id = %s AND ativo = true",
                (user_id,)
            )
            row = cur.fetchone()

    if not row:
        return error(404, "Usuário não encontrado")

    return success(200, {"id": row[0], "nome": row[1], "email": row[2], "criado_em": str(row[3])})


def create_user(event):
    """Cria um novo usuário."""
    body = json.loads(event["body"])

    if not body.get("nome") or not body.get("email"):
        return error(400, "Campos 'nome' e 'email' são obrigatórios")

    new_id = str(uuid.uuid4())

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuarios (id, nome, email) VALUES (%s, %s, %s)",
                (new_id, body["nome"], body["email"])
            )
        conn.commit()

    return success(201, {"id": new_id, "mensagem": "Usuário criado com sucesso"})


def update_user(event):
    """Atualiza nome e email de um usuário existente."""
    user_id = event["pathParameters"]["id"]
    body    = json.loads(event["body"])

    if not body.get("nome") or not body.get("email"):
        return error(400, "Campos 'nome' e 'email' são obrigatórios")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE usuarios SET nome = %s, email = %s WHERE id = %s AND ativo = true",
                (body["nome"], body["email"], user_id)
            )
            if cur.rowcount == 0:
                return error(404, "Usuário não encontrado")
        conn.commit()

    return success(200, {"mensagem": "Usuário atualizado com sucesso"})


def delete_user(event):
    """Soft delete — marca o usuário como inativo."""
    user_id = event["pathParameters"]["id"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE usuarios SET ativo = false WHERE id = %s AND ativo = true",
                (user_id,)
            )
            if cur.rowcount == 0:
                return error(404, "Usuário não encontrado")
        conn.commit()

    return success(200, {"mensagem": "Usuário removido com sucesso"})