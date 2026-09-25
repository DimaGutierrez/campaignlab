# Setup

**[Open the public browser demo →](https://diegogutierrez.pages.dev/campaignlab/)** — fictional campaigns, simulated clicks and conversions, no installation or backend connection. The technical guides below describe the complete local backend. [Public demo scope](https://github.com/DimaGutierrez/campaignlab/blob/main/docs/public-demo.md).

Requires Python 3.12+. No Node build or external database is required. Node is only used for optional JavaScript syntax checking.

## Native: PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:ADMIN_KEY = python -c "import secrets; print(secrets.token_urlsafe(32))"
$env:INGEST_KEY = python -c "import secrets; print(secrets.token_urlsafe(32))"
$env:PUBLIC_URL = 'http://127.0.0.1:8010'
python seed.py --demo
uvicorn app:app --host 127.0.0.1 --port 8010 --no-access-log
```

Use the generated admin key to connect the dashboard. Keep it private. The ingestion key is for your application backend. To inspect the admin value locally before starting the server, use `$env:ADMIN_KEY`; never paste it in an issue or a screenshot.

## Native: macOS/Linux

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ADMIN_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export INGEST_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export PUBLIC_URL=http://127.0.0.1:8010
python seed.py --demo
uvicorn app:app --host 127.0.0.1 --port 8010 --no-access-log
```

Native startup reads environment variables, not `.env`. Demo seeding is optional and refuses non-empty databases. SQLite persists at `data/campaignlab.db`; use `DATABASE_PATH` to choose a different location. Stop the server before copying the database for a simple consistent backup.

## Docker

Copy `.env.example` to `.env`, replace both placeholder keys with independent random values of at least 24 characters, and run `docker compose up --build`. Run `docker compose exec app python seed.py --demo` once if you want fictional data. Data lives in the named volume. Never delete a volume to upgrade the app.

## Destination integration

The destination does not automatically create conversions. Your landing application must capture `cl_click`, associate it with its own order flow, and submit a backend request described in the README. Do not put the ingestion key in browser code. Store/reuse the same order event ID for retries. If the backend response is lost, retry the exact payload.

## Public hosting checklist

The default configuration is local only. Before exposing it: configure HTTPS, set PUBLIC_URL to the canonical origin, put request limits/rate limits at the reverse proxy, rotate placeholder keys, set a data-retention policy, back up SQLite, and consider bots/link-preview traffic. Redact query strings from proxy/destination logs. Keys give workspace-wide access; there is no per-user login. Review destination URLs before sharing them. The app only redirects; it never fetches destinations itself.
