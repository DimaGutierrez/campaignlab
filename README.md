# CampaignLab

**[Open the live demo →](https://diegogutierrez.pages.dev/campaignlab/)**

https://diegogutierrez.pages.dev/campaignlab/

No installation or account required. Hosted on Cloudflare Pages, with fictional data and browser-only simulation. Campaigns and simulated events stay in your browser. The full Python backend is available in this repository.

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

## Try it online

Open **[CampaignLab](https://diegogutierrez.pages.dev/campaignlab/)** to create a sample campaign, copy UTM links, simulate a click and conversion, retry the same event without duplicating revenue, or export demo data.

The public demo does not collect real clicks or call the Python API. See [public demo details](docs/public-demo.md).

## Run the fullstack application yourself

For the real tracking API and persistent SQLite database, follow the [local installation guide](docs/setup.md). It includes native Python and Docker instructions, private key configuration and the local development address.

## Backend conversion contract

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
