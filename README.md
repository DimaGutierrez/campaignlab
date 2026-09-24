# CampaignLab

**[Probar demo online / Try the live demo](https://campaignlab-demo.pages.dev/)** — Datos ficticios y simulación en el navegador; el backend real está en este repositorio.

![CampaignLab — marketing with evidence](assets/hero-v2.png)

**Create UTM links, record conversions and explain your campaign metrics.** A small fullstack marketing workspace built with FastAPI, SQLite and browser-native JavaScript.

English · [Español](README.es.md) · [Setup](docs/setup.md) · [Architecture](docs/architecture.md) · [Metrics](docs/metrics.md)

## Why this exists

A dashboard can look convincing while counting the wrong thing. CampaignLab makes the path explicit: a tracking link creates a click ID; your backend submits a conversion against it; repeated event IDs cannot inflate revenue.

## Included

- Campaign creation with validated UTM naming and HTTPS destinations.
- Redirect links that preserve unrelated query parameters.
- Authenticated server-to-server conversion ingestion, a 30-day click window, and idempotent event IDs.
- Campaign comparison, recorded revenue, conversion rate, ROAS and CSV export.
- Separate admin and ingestion keys; no third-party scripts, tracking cookies or IP storage in the application database.
- Fictional demo data, tests, Docker configuration and community documentation.

## Run locally

```sh
python -m venv .venv
# Activate the environment; see docs/setup.md for your operating system.
pip install -r requirements.txt
```

Set two different random environment variables, `ADMIN_KEY` and `INGEST_KEY`, each at least 24 characters. Then:

```sh
python seed.py --demo  # optional; only accepts an empty database
uvicorn app:app --host 127.0.0.1 --port 8010 --no-access-log
```

Open **http://127.0.0.1:8010** and enter your admin key. Demo numbers are synthetic and must not be presented as business results. The native launcher does not automatically load `.env`.

For Docker, copy `.env.example` to `.env`, replace both keys, then `docker compose up --build`. The default port binds only to loopback. See [setup](docs/setup.md) before hosting publicly.

## Conversion contract

The destination receives `cl_click` alongside the UTM parameters. Preserve that value in your own application and submit from your backend, never by exposing the ingestion key in frontend code:

```http
POST /api/conversions
X-Ingest-Key: <server-side key>
Content-Type: application/json

{"event_id":"order_unique_001","click_id":"<value received by your landing page>","revenue_cents":4900}
```

First write: **201**. Same event and payload: **200** replay. Same event with another payload: **409**. Unknown or older-than-30-days click: **422**. Revenue uses integer USD cents.

## What the metrics mean

Conversion rate is **distinct converted clicks / recorded clicks**, not events / people. ROAS is **recorded attributed revenue / manually declared spend**. Zero denominators display “—”. These are all-time descriptive figures, not causal lift, profit, unique visitors, or verified ad-platform results. Bots and link-preview crawlers can inflate clicks.

## Validation

```sh
pip install -r requirements-dev.txt
pytest -q
ruff check .
node --check web/app.js
```

See [verification](docs/verification.md) for actual results and [limitations](docs/metrics.md). The workflow runs Python checks and a Docker health check after publication; a workflow file is not evidence of a completed remote run.

## Participate

Join [Discussions](https://github.com/DimaGutierrez/campaignlab/discussions) and read the [Wiki](https://github.com/DimaGutierrez/campaignlab/wiki). Versioned source copies live in discussions/ and wiki/.

- [What counts as a conversion?](https://github.com/DimaGutierrez/campaignlab/discussions/1)
- [How do you prevent duplicate revenue?](https://github.com/DimaGutierrez/campaignlab/discussions/2)
- [What should we build next?](https://github.com/DimaGutierrez/campaignlab/discussions/3)

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [MIT license](LICENSE)

Built by Diego Gutierrez to connect marketing experience with backend engineering. This version is a single-workspace prototype: no ad-network integrations, billing, account management, spend editing, refunds or multi-touch attribution.

## Preview / Vista previa

![Actual dashboard with fictional data](assets/dashboard.png)

[Mobile screenshot](assets/mobile.png). These are application screenshots, not business results.
