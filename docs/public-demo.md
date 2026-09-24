# Public demo on Cloudflare Pages

Live: https://campaignlab-demo.pages.dev/

Deployment 18372ef0 succeeded with `uses_functions: false`. Public HTTPS browser verification passed for loading, simulated click/conversion, duplicate replay and persistence after reload.

The `demo/` directory is a separate static, browser-only showcase. It contains no FastAPI server, database, API keys, Workers Functions, remote event collection or connection to the developer's PC.

Visitors can create fictional campaigns, copy ordinary UTM links, simulate clicks and conversions, replay a simulated event, export demo CSV data and reset their own browser data. Changes are stored in localStorage under `campaignlab-public-demo-v1`; if storage is blocked, the app falls back to memory. Data is not shared between visitors or devices. Do not enter private customer information.

The simulator demonstrates idempotency in browser memory; it is not a replacement for the transactional Python backend. Its 201/200 labels are illustrative, not HTTP responses. The public demo does not implement the backend's 30-day attribution window or real tracked redirects. UTM links go directly to the destination and record nothing in CampaignLab.

## Build and verify

```sh
python scripts/build_demo.py
node --test tests/demo-model.test.mjs
python -m http.server 8011 --bind 127.0.0.1 --directory demo
```

The build reuses the existing application shell and CSS while keeping the fullstack application's authentication and API unchanged. Six Node tests cover initial totals, zero denominators, event replay/conflict, distinct converted clicks, URL validation, CSV formula escaping and invalid input.

## Deployment

Upload only the six files in `demo/` to a Cloudflare Pages Direct Upload project. The supplied `_headers` file blocks outbound fetch requests with `connect-src 'none'`. The project uses the included free `pages.dev` subdomain; no purchased domain, paid plan, database, Functions or Tunnel is needed. Static asset requests are free under Cloudflare's current Pages pricing. Cloudflare still serves the files and may process standard hosting request metadata; this is not a claim of zero infrastructure logging.

Do not upload the repository root, `.env`, `data/`, private preview keys or the backend. Direct Upload does not automatically deploy later GitHub changes: rebuild and upload `demo/` for each release. Do not enable Functions or other paid services without reviewing costs.

References: [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/), [Pages pricing](https://developers.cloudflare.com/pages/functions/pricing/).
