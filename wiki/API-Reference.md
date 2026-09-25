# API reference

**[Open the public browser demo →](https://diegogutierrez.pages.dev/campaignlab/)** — fictional campaigns, simulated clicks and conversions, no installation or backend connection. The technical guides below describe the complete local backend. [Public demo scope](https://github.com/DimaGutierrez/campaignlab/blob/main/docs/public-demo.md).

| Route | Credential | Purpose |
| --- | --- | --- |
| GET /health | None | Database readiness |
| POST /api/campaigns | X-Admin-Key | Create validated campaign |
| GET /api/campaigns | X-Admin-Key | All-time metrics and links |
| GET /api/export.csv | X-Admin-Key | Export formula-escaped CSV |
| GET /r/{id} | None | Record click, redirect with UTM and cl_click |
| POST /api/conversions | X-Ingest-Key | Record or replay a conversion |

Campaign body: name, destination (HTTPS), source, medium, campaign, spend_cents. UTM labels accept lowercase letters, numbers, hyphens and underscores. Amounts are nonnegative integer USD cents.

Conversion body: event_id (8–100 letters, numbers, underscores or hyphens), click_id, revenue_cents. 201 means recorded; 200 means identical retry; 409 means reused event ID with a different payload; 422 means validation failure or unknown/expired click. Keys are independent server configuration. Missing/wrong keys return 401; missing/short server configuration returns 503.

The frontend stores its admin key only in memory. It never receives the ingestion key. Destination applications must submit conversion events from their own backend.
