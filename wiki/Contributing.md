# Contributing

**[Open the public browser demo →](https://diegogutierrez.pages.dev/campaignlab/)** — fictional campaigns, simulated clicks and conversions, no installation or backend connection. The technical guides below describe the complete local backend. [Public demo scope](https://github.com/DimaGutierrez/campaignlab/blob/main/docs/public-demo.md).

Start with a concrete user problem and a reproducible example using fictional data. Small changes to documentation, accessibility and edge-case tests are welcome.

Run `pip install -r requirements-dev.txt`, `pytest -q`, `ruff check .` and `node --check web/app.js`. Use an isolated SQLite database for experiments. Never commit `.env`, customer data, keys or runtime databases.

For metric changes, explain numerator, denominator, attribution window and treatment of retries. A new dashboard number needs a definition and a test. For schema changes, include a forward migration and backup instructions. See SECURITY.md for sensitive reports.
