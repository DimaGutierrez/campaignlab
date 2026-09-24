"""CampaignLab: transparent, click-based campaign attribution."""
import csv
import hmac
import io
import os
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).parent
DB_PATH = os.getenv("DATABASE_PATH", str(ROOT / "data/campaignlab.db"))
ADMIN_KEY = os.getenv("ADMIN_KEY", "")
INGEST_KEY = os.getenv("INGEST_KEY", "")
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://127.0.0.1:8010").rstrip("/")
app = FastAPI(title="CampaignLab", version="0.1.0", docs_url=None, redoc_url=None)


@contextmanager
def db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    try:
        with con:
            yield con
    finally:
        con.close()


def initialize():
    with db() as con:
        con.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS campaigns (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, destination TEXT NOT NULL,
            source TEXT NOT NULL, medium TEXT NOT NULL, campaign TEXT NOT NULL,
            spend_cents INTEGER NOT NULL CHECK(spend_cents >= 0),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY, campaign_id TEXT NOT NULL REFERENCES campaigns(id),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS clicks_campaign ON clicks(campaign_id);
        CREATE TABLE IF NOT EXISTS conversions (
            event_id TEXT PRIMARY KEY, click_id TEXT NOT NULL REFERENCES clicks(id),
            revenue_cents INTEGER NOT NULL CHECK(revenue_cents >= 0),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS conversions_click ON conversions(click_id);
        """)


initialize()


def authorize(value, expected):
    if len(expected) < 24:
        raise HTTPException(503, "Configure a key of at least 24 characters")
    if not value or not hmac.compare_digest(value.encode(), expected.encode()):
        raise HTTPException(401, "Invalid API key")


def admin(x_admin_key: str | None = Header(default=None)):
    authorize(x_admin_key, ADMIN_KEY)


class Campaign(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    destination: str = Field(min_length=8, max_length=1500)
    source: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")
    medium: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")
    campaign: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")
    spend_cents: int = Field(default=0, ge=0, le=100_000_000)


class Conversion(BaseModel):
    event_id: str = Field(pattern=r"^[a-zA-Z0-9_-]{8,100}$")
    click_id: str = Field(min_length=20, max_length=100)
    revenue_cents: int = Field(ge=0, le=100_000_000)


@app.middleware("http")
async def headers(request: Request, call_next):
    length = request.headers.get("content-length", "0")
    if not length.isdecimal() or int(length) > 8192:
        return Response("Request too large", 413)
    if request.method in {"POST", "PATCH"}:
        body = await request.body()
        if len(body) > 8192:
            return Response("Request too large", 413)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    if request.url.path.startswith(("/api/", "/r/")):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
def health():
    with db() as con:
        con.execute("SELECT 1").fetchone()
    return {"status": "ok"}


def tagged_url(row, click_id=None):
    url = urlsplit(row["destination"])
    params = [(k, v) for k, v in parse_qsl(url.query, keep_blank_values=True)
              if k not in {"utm_source", "utm_medium", "utm_campaign", "cl_click"}]
    params.extend([(f"utm_{key}", row[key]) for key in ("source", "medium", "campaign")])
    if click_id:
        params.append(("cl_click", click_id))
    return urlunsplit((url.scheme, url.netloc, url.path, urlencode(params), url.fragment))


@app.post("/api/campaigns", dependencies=[Depends(admin)], status_code=201)
def create_campaign(data: Campaign):
    try:
        url = urlsplit(data.destination)
        hostname = url.hostname
        _ = url.port
    except ValueError:
        raise HTTPException(422, "Invalid destination") from None
    if url.scheme != "https" or not hostname or url.username or url.password:
        raise HTTPException(422, "Destination must be an HTTPS URL without credentials")
    if any(c in data.destination for c in "\r\n\\"):
        raise HTTPException(422, "Invalid destination")
    values = data.model_dump()
    values["name"] = data.name.strip()
    if not values["name"]:
        raise HTTPException(422, "Name is required")
    cid = secrets.token_urlsafe(12)
    with db() as con:
        con.execute("""INSERT INTO campaigns
            (id,name,destination,source,medium,campaign,spend_cents)
            VALUES (:id,:name,:destination,:source,:medium,:campaign,:spend_cents)""",
            {"id": cid, **values})
    return {"id": cid, "tracking_url": f"{PUBLIC_URL}/r/{cid}",
            "utm_url": tagged_url(values)}


def metrics():
    with db() as con:
        rows = con.execute("""SELECT c.*,
            (SELECT COUNT(*) FROM clicks k WHERE k.campaign_id=c.id) clicks,
            (SELECT COUNT(*) FROM conversions v JOIN clicks k ON k.id=v.click_id
                WHERE k.campaign_id=c.id) conversions,
            (SELECT COUNT(DISTINCT v.click_id) FROM conversions v
                JOIN clicks k ON k.id=v.click_id WHERE k.campaign_id=c.id) converted_clicks,
            COALESCE((SELECT SUM(v.revenue_cents) FROM conversions v
                JOIN clicks k ON k.id=v.click_id WHERE k.campaign_id=c.id),0) revenue_cents
            FROM campaigns c ORDER BY c.created_at DESC, c.id""").fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item.update(tracking_url=f"{PUBLIC_URL}/r/{row['id']}", utm_url=tagged_url(row))
        item["conversion_rate"] = row["converted_clicks"] / row["clicks"] if row["clicks"] else None
        item["roas"] = row["revenue_cents"] / row["spend_cents"] if row["spend_cents"] else None
        result.append(item)
    return result


@app.get("/api/campaigns", dependencies=[Depends(admin)])
def list_campaigns():
    return {"campaigns": metrics(), "currency": "USD", "scope": "all-time"}


@app.get("/r/{campaign_id}")
def redirect(campaign_id: str):
    with db() as con:
        row = con.execute("SELECT * FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Campaign not found")
        click = secrets.token_urlsafe(24)
        con.execute("INSERT INTO clicks(id,campaign_id) VALUES (?,?)", (click, campaign_id))
        target = tagged_url(row, click)
    return RedirectResponse(target, status_code=302)


@app.post("/api/conversions")
def convert(data: Conversion, response: Response, x_ingest_key: str | None = Header(default=None)):
    authorize(x_ingest_key, INGEST_KEY)
    with db() as con:
        con.execute("BEGIN IMMEDIATE")
        prior = con.execute("SELECT * FROM conversions WHERE event_id=?", (data.event_id,)).fetchone()
        if prior:
            if prior["click_id"] != data.click_id or prior["revenue_cents"] != data.revenue_cents:
                raise HTTPException(409, "Event ID already has a different payload")
            return {"event_id": data.event_id, "replayed": True}
        click = con.execute("SELECT id FROM clicks WHERE id=? AND created_at >= datetime('now','-30 days')",
                            (data.click_id,)).fetchone()
        if not click:
            raise HTTPException(422, "Unknown or expired click (30-day attribution window)")
        con.execute("INSERT INTO conversions(event_id,click_id,revenue_cents) VALUES (?,?,?)",
                    (data.event_id, data.click_id, data.revenue_cents))
    response.status_code = 201
    return {"event_id": data.event_id, "replayed": False}


@app.get("/api/export.csv", dependencies=[Depends(admin)])
def export():
    buffer = io.StringIO(newline="")
    fields = ["name", "source", "medium", "campaign", "clicks", "conversions",
              "converted_clicks", "spend_cents", "revenue_cents", "conversion_rate", "roas"]
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for row in metrics():
        for key, value in row.items():
            if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                row[key] = "'" + value
        writer.writerow(row)
    return Response(buffer.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="campaignlab.csv"'})


app.mount("/", StaticFiles(directory=ROOT / "web", html=True), name="web")
