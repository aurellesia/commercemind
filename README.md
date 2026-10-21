# Ecommerce Monorepo

This is a simple ecommerce project with a FastAPI backend, PostgreSQL database, and SvelteKit frontend.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL
- Frontend: SvelteKit
- Local services: Docker Compose

## Project Structure

```text
.
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── requirements.txt
├── frontend/
├── docs/
│   └── architecture_notes.md
├── docker-compose.yml
└── README.md
```

## Requirements

- Python 3.8+
- Node.js and npm
- Docker and Docker Compose

## Database Setup

Start PostgreSQL:

```bash
docker-compose up -d
```

Default database connection:

```text
Host: localhost
Port: 5432
Database: mydb
Username: myuser
Password: mypassword
```

Apply database migrations:

```bash
backend/venv/bin/alembic upgrade head
```

If you are connecting an existing local database that was previously created with SQLAlchemy `create_all`, stamp the existing schema first, then upgrade:

```bash
backend/venv/bin/alembic stamp 20260424_0001
backend/venv/bin/alembic upgrade head
```

## Backend Setup

Create and activate a virtual environment:

```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Run the backend from the project root:

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Product API

Available product routes:

- `POST /products/`
- `GET /products/`
- `GET /products/{product_id}`
- `PUT /products/{product_id}`
- `DELETE /products/{product_id}`

Example product body:

```json
{
  "name": "Facial Wash",
  "description": "Facial wash for normal skin",
  "price": 50000
}
```

## Frontend Setup

Install dependencies:

```bash
cd frontend
npm install
```

Run the frontend:

```bash
npm run dev
```

## Development Notes

- Backend schema is managed with Alembic migrations.
- Keep backend API settings in an `.env` file once configuration grows.
- See `docs/architecture_notes.md` for architecture notes.
