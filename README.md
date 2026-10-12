# Axiom

Gerador de arte matemática com React, FastAPI, NumPy e Pillow.

## Estado atual

A Milestone 1 estabelece a fundação do projeto:

- API FastAPI com health check em `GET /api/health`;
- configuração por variáveis de ambiente e CORS;
- aplicação React + TypeScript com Vite;
- verificação visual da conexão com a API;
- testes, lint e type-check básicos.

Banco de dados e motor de renderização serão adicionados nas próximas milestones.

## Requisitos

- Python 3.12 ou superior;
- Node.js 20 ou superior;
- npm 10 ou superior.

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload
```

A API estará em `http://localhost:8000` e sua documentação em
`http://localhost:8000/docs`.

Para usar um arquivo de ambiente:

```bash
cp .env.example .env
uvicorn app.main:app --reload --env-file .env
```

### Verificações do backend

```bash
cd backend
pytest
ruff check .
ruff format --check .
```

## Frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

O frontend estará em `http://localhost:5173`. Durante o desenvolvimento, o
Vite encaminha requisições iniciadas por `/api` para `http://localhost:8000`.

Defina `VITE_API_URL` somente quando o backend estiver em outro endereço:

```bash
cp .env.example .env
```

### Verificações do frontend

```bash
cd frontend
npm run lint
npm run test
npm run build
```

## Configuração

### Backend

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `APP_NAME` | `Axiom API` | Nome exibido no OpenAPI |
| `ENVIRONMENT` | `development` | Ambiente atual |
| `API_PREFIX` | `/api` | Prefixo das rotas HTTP |
| `CORS_ORIGINS` | `http://localhost:5173` | Origens permitidas, separadas por vírgula |

### Frontend

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `VITE_API_URL` | vazio | URL absoluta opcional do backend |

## Estrutura

```text
backend/
├── app/
│   ├── api/
│   ├── config.py
│   └── main.py
├── tests/
└── pyproject.toml

frontend/
├── src/
│   ├── api/
│   ├── test/
│   ├── App.tsx
│   └── main.tsx
└── package.json
```
