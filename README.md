# fastapi-mongodb-crud

Full-stack CRUD application built using FastAPI, MongoDB, and Vanilla JavaScript with REST API integration.

## Features

- FastAPI REST API for create, read, update, and delete operations
- MongoDB-backed persistence for items
- Vanilla JavaScript frontend consuming REST endpoints

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 in your browser.

## API Endpoints

- `GET /api/items`
- `POST /api/items`
- `GET /api/items/{item_id}`
- `PUT /api/items/{item_id}`
- `DELETE /api/items/{item_id}`

## Environment Variables

- `MONGODB_URL` (default: `mongodb://localhost:27017`)
- `MONGODB_DB` (default: `fastapi_crud`)

## Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```
