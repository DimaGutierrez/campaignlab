# Metric definitions and boundaries

**[Open the public browser demo →](https://diegogutierrez.pages.dev/campaignlab/)** — fictional campaigns, simulated clicks and conversions, no installation or backend connection. The technical guides below describe the complete local backend. [Public demo scope](https://github.com/DimaGutierrez/campaignlab/blob/main/docs/public-demo.md).

| Metric | Definition |
| --- | --- |
| Clicks | Successful GET requests to a campaign redirect, including repeat visits and possible bots |
| Conversions | Distinct accepted event IDs; multiple events may belong to one click |
| Converted clicks | Distinct click IDs with at least one accepted conversion |
| Conversion rate | Converted clicks divided by recorded clicks; null if no clicks |
| Revenue | Sum of reported conversion amounts in integer USD cents |
| Spend | Manually declared, fixed campaign spend in USD cents |
| ROAS | Recorded revenue divided by declared spend; null if spend is zero |

Totals cover the entire retained database. Attribution accepts a known click from the preceding 30 days (UTC). Replaying an already recorded event after that window still returns its existing outcome. There is no cross-device, person-level, multi-touch or ad-platform identity matching. The caller chooses which click ID it preserves; CampaignLab does not automatically infer first-touch or last-touch.

No statistical significance, causal lift, profit, currency conversion, refunds, bot filtering or deduplication of people is claimed. ROAS can be incomplete or misleading if event delivery or declared spend is incomplete. A tracked click is a request, not proof a human saw a landing page. The app does not automatically purge records; establish retention before public use.
