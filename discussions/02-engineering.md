# Your webhook retries six times. Does your revenue grow six times?

**[Open the public browser demo →](https://diegogutierrez.pages.dev/campaignlab/)** — fictional campaigns, simulated clicks and conversions, no installation or backend connection. The technical guides below describe the complete local backend. [Public demo scope](https://github.com/DimaGutierrez/campaignlab/blob/main/docs/public-demo.md).

![Your webhook retries six times. Does your revenue grow six times?](https://github.com/DimaGutierrez/campaignlab/raw/refs/heads/main/assets/discussion-engineering-v2.png)

A lost HTTP response should not create six sales. CampaignLab uses a unique event ID, payload comparison and a SQLite transaction. The same payload replays; a conflicting payload returns 409.

**How would you test the failure between committing a conversion and delivering the response?** Share your expected result and the invariant your test protects.

The repository includes concurrent retry tests. For this single-instance scope, would you keep SQLite or choose PostgreSQL? Explain the tradeoff.

Respuestas en español bienvenidas. No compartas claves ni datos de clientes.
