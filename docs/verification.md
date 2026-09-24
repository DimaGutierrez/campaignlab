# Verification

Local Python integration tests: **11 passed**, using isolated SQLite databases. Covered authentication boundaries, UTM replacement/preservation, end-to-end attribution, identical retries, conflicting payloads, six concurrent retry requests, expiry, invalid destinations, empty denominators, formula-safe CSV and basic input limits.

JavaScript syntax check passed. Python lint passed. Browser verification completed: authenticated dashboard load, expected synthetic totals (400 clicks, 38 events, USD 2,180 revenue), campaign creation from the form and updated zero-denominator display. Desktop and 390px mobile layouts were visually inspected. Screenshots contain fictional data. CSV semantics are covered by API tests; downloading a CSV in the browser was not separately tested.

One upstream Starlette TestClient deprecation warning is emitted by the installed HTTP test adapter. It does not fail these tests.

Docker was not run locally (Docker is unavailable). GitHub Actions passed both the Python/JavaScript checks and the Docker build/startup health check on 2026-09-24: [verified run](https://github.com/DimaGutierrez/campaignlab/actions/runs/36004768322), commit 688a094f9622200d8a5a0b30dab3f7717dbff60b. These tests are not a production security review, load test or proof of marketing outcomes.
