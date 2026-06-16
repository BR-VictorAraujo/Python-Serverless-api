# python-serverless-api

API REST serverless construída com Python, AWS Lambda, API Gateway e PostgreSQL (RDS).

## Tecnologias

- Python 3.11
- AWS Lambda
- AWS API Gateway
- AWS RDS PostgreSQL
- AWS SAM (Serverless Application Model)
- pg8000 (driver PostgreSQL puro Python)

## Arquitetura

Cliente → API Gateway → Lambda (Python) → RDS PostgreSQL

## Endpoints

### Criar usuário
```http
POST /users
Content-Type: application/json

{
  "nome": "Victor Araujo",
  "email": "victor@email.com"
}
```

### Listar usuários
```http
GET /users
```

### Buscar usuário por ID
```http
GET /users/{id}
```

### Atualizar usuário
```http
PUT /users/{id}
Content-Type: application/json

{
  "nome": "Victor Atualizado",
  "email": "victor.novo@email.com"
}
```

### Deletar usuário
```http
DELETE /users/{id}
```

## Como executar

### Pré-requisitos
- Python 3.11
- AWS CLI configurado
- AWS SAM CLI

### Deploy
```bash
sam build
sam deploy
```

## Variáveis de ambiente

Copie o `.env.example` e preencha com suas credenciais.

| Variável | Descrição |
|---|---|
| DB_HOST | Endpoint do RDS PostgreSQL |
| DB_NAME | Nome do banco de dados |
| DB_USER | Usuário do banco |
| DB_PASSWORD | Senha do banco |
| DB_PORT | Porta (padrão: 5432) |