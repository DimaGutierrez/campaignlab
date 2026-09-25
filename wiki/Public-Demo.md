# Public demo on Cloudflare Pages

Live: https://diegogutierrez.pages.dev/campaignlab/

The demo is hosted under the portfolio at `/campaignlab/`. The former `campaignlab-demo.pages.dev` address redirects to the new location. No backend service or Pages Functions are used.

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

Copy `index.html`, `app.js`, `model.mjs`, `style.css` and `404.html` from `demo/` into the portfolio's `campaignlab/` directory. Preserve every existing portfolio file, including SlotGuard and Webhook Lab. Merge the demo's `_headers` policy under `/campaignlab/*` in the portfolio root rather than replacing the root configuration. It blocks outbound fetch requests with `connect-src 'none'`. Asset references are relative, so the demo works within the subdirectory.

The route is absent from the portfolio menu and sitemap and has a `noindex` directive. Anyone with its link can open it; unlisted navigation is not access control. No purchased domain, paid plan, database, Functions or Tunnel is needed. Cloudflare still serves the files and may process standard hosting request metadata; this is not a claim of zero infrastructure logging.

Browser storage is scoped to the website origin. Sample campaigns saved under the old hostname do not automatically move to the portfolio hostname; the new location starts with its own example data. The old site redirects without uploading or transferring visitor data.

Do not upload the repository root, `.env`, `data/`, private preview keys or the backend. Direct Upload does not automatically deploy later GitHub changes: rebuild and deploy the complete portfolio bundle for each release. Never publish only the CampaignLab folder as the portfolio's entire deployment.

References: [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/), [Pages pricing](https://developers.cloudflare.com/pages/functions/pricing/).
