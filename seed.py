"""Deterministic fictional demo. Never run against production data."""
import argparse

import app

parser = argparse.ArgumentParser()
parser.add_argument("--demo", action="store_true", required=True)
parser.parse_args()
with app.db() as con:
    if con.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]:
        raise SystemExit("Refusing to seed a non-empty database")
    for cid, name, source, medium, spend, clicks, converted, revenue in [
        ("demo-linkedin", "Spring launch · LinkedIn", "linkedin", "paid-social", 24000, 120, 12, 72000),
        ("demo-newsletter", "The Friday edit", "newsletter", "email", 6000, 80, 16, 96000),
        ("demo-search", "Intent-first search", "google", "cpc", 42000, 200, 10, 50000),
    ]:
        con.execute("INSERT INTO campaigns(id,name,destination,source,medium,campaign,spend_cents) VALUES (?,?,?,?,?,?,?)",
                    (cid, name, "https://example.com/", source, medium, "spring-launch", spend))
        for i in range(clicks):
            token = f"synthetic-{cid}-click-{i:04d}"
            con.execute("INSERT INTO clicks(id,campaign_id) VALUES (?,?)", (token, cid))
            if i < converted:
                con.execute("INSERT INTO conversions(event_id,click_id,revenue_cents) VALUES (?,?,?)",
                            (f"synthetic-{cid}-{i}", token, revenue // converted))
print("Seeded 3 campaigns with fictional USD data. No external services were contacted.")
