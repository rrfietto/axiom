# Axiom

Gerador de arte matemática com React, FastAPI, NumPy e Pillow.

## Estado atual

As três primeiras milestones estabelecem a fundação e o motor inicial:

- API FastAPI com health check em `GET /api/health`;
- configuração por variáveis de ambiente e CORS;
- aplicação React + TypeScript com Vite;
- verificação visual da conexão com a API;
- contratos imutáveis de renderer, parâmetros e contexto;
- registry explícito e engine de execução isolada;
- primeiro renderer `wave-field`, determinístico por seed, com NumPy e Pillow;
- presets persistidos em SQLite com SQLAlchemy e migrações Alembic;
- endpoints públicos `GET /api/presets` e `GET /api/presets/{slug}`;
- renderização PNG por `POST /api/render`;
- testes, lint e type-check básicos.

A persistência e a galeria de artworks serão adicionadas nas próximas milestones.

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
alembic upgrade head
uvicorn app.main:app --reload
```

A API estará em `http://localhost:8000` e sua documentação em
`http://localhost:8000/docs`. A migração cria `data/app.db` e insere o preset
inicial `emerald-waves`.

Para usar um arquivo de ambiente:

```bash
cp .env.example .env
uvicorn app.main:app --reload --env-file .env
```

### Renderização

Exemplo de requisição:

```bash
curl -X POST http://localhost:8000/api/render \
  -H 'Content-Type: application/json' \
  -d '{"preset_slug":"emerald-waves","width":800,"height":800,"seed":42,"parameters":{}}' \
  --output axiom.png
```

Os parâmetros omitidos usam os defaults do preset. A resposta é uma imagem PNG.

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
| `DATABASE_URL` | `sqlite:///.../data/app.db` | URL de conexão SQLAlchemy |

### Frontend

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `VITE_API_URL` | vazio | URL absoluta opcional do backend |

## Estrutura

```text
backend/
├── app/
│   ├── api/
│   ├── db/
│   ├── rendering/
│   ├── schemas/
│   ├── services/
│   ├── config.py
│   └── main.py
├── migrations/
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
