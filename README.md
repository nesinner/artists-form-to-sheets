# Artist Submissions Portal

Streamlit app for artist submissions, admin review, releases, and planned catalog.

## Requirements
- Python 3.11+

## Setup
```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## Environment
Create a `.env` file in the project root:
```
ADMIN_BOOTSTRAP_EMAIL=admin@example.com
ADMIN_BOOTSTRAP_PASSWORD=change_me
DB_URL=sqlite:///data/app.db
UPLOAD_DIR=data/uploads
APP_BASE_URL=http://localhost:8501
```
Or set the same keys in Streamlit Secrets (TOML).

## Persistent storage (Postgres)
Streamlit Community Cloud uses ephemeral disk, so SQLite files reset after sleep.
Use an external Postgres database for persistent data.

1) Create a Postgres database (Neon, Supabase, Render, etc.).
2) Set `DB_URL` to the connection string, for example:
```
postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
```
3) Put the same `DB_URL` into Streamlit Secrets or `.env` and restart the app.

## Run
```bash
streamlit run main.py
```

## Auth
- Users must register or log in before accessing the portal.
- To create the initial admin user, set `ADMIN_BOOTSTRAP_EMAIL` and
  `ADMIN_BOOTSTRAP_PASSWORD` in `.env` and restart the app.

## Test
```bash
pytest -q
```

## CSV export check (CLI)
```bash
python scripts/check_csv.py
```
