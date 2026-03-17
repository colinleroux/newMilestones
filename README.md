# deeds

`deeds` is a small goal-and-step tracker. You can create goals, break them into achievable steps, complete those steps, and reflect on progress.

## Linux Setup

### Run With Docker

From a fresh clone:

```bash
docker compose build
docker compose up -d
```

Then open:

```bash
http://localhost
```

To stop the app:

```bash
docker compose down
```

Notes:

- Vite frontend assets are built during `docker compose build`
- the database is created automatically on startup by `flask db upgrade`
- SQLite data lives under `instance/site.db`

### Run Without Docker

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set the Flask app and create the database schema:

```bash
export FLASK_APP=wsgi_app.py
python -m flask db upgrade
```

Run the app:

```bash
python run.py
```

## Fresh Database

On a clean copy of the repo, you should not need to copy any existing `site.db` file.

The expected flow is:

1. clone the repository
2. run `flask db upgrade` directly or start with Docker
3. let SQLite create `instance/site.db`
4. the migration files in `migrations/` build the schema

## Useful Commands

Rebuild containers:

```bash
docker compose build
```

Restart in the background:

```bash
docker compose up -d
```

Stop containers:

```bash
docker compose down
```
