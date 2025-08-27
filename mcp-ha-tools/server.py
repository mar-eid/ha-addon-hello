import os
import json
import logging
from typing import Dict, Any, List, Optional

import httpx
import psycopg2
from psycopg2.extras import RealDictCursor

from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

# ---------------------------
# Environment / configuration
# ---------------------------
HA_URL = os.environ.get("HA_URL", "http://homeassistant:8123").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

DB_HOST = os.environ.get("DB_HOST", "core-postgres")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "homeassistant")
DB_USER = os.environ.get("DB_USER", "ha_reader")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_CONNECT_TIMEOUT = int(os.environ.get("DB_CONNECT_TIMEOUT", "5"))  # seconds

# Safety toggle: default False (read-only)
ENABLE_WRITE = str(os.environ.get("ENABLE_WRITE", "false")).lower() == "true"

# -------------
# Validations
# -------------
if not HA_TOKEN:
    raise RuntimeError("HA_TOKEN (Supervisor or Long-Lived Token) is required.")

# -------------
# Logging setup
# -------------
valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"}
level = getattr(logging, LOG_LEVEL, logging.INFO) if LOG_LEVEL in valid_levels else logging.INFO

logging.basicConfig(
    level=level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("mcp-ha-tools")

logger.info(
    "Starting MCP HA Tools Server (log_level=%s, ha_url=%s, db_host=%s, db_port=%s, db_name=%s, db_user=%s, enable_write=%s)",
    LOG_LEVEL, HA_URL, DB_HOST, DB_PORT, DB_NAME, DB_USER, ENABLE_WRITE
)

# -------------------------------------------
# DB helper: connect with read-only by default
# -------------------------------------------
def _db_connect():
    """
    Create a PostgreSQL/Timescale connection.
    - If ENABLE_WRITE is False: read-only + autocommit
    - If ENABLE_WRITE is True: read-write (autocommit OFF by default)
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=DB_CONNECT_TIMEOUT,
        application_name="mcp_ha_tools_server"
    )
    if not ENABLE_WRITE:
        # Read-only session, autocommit (no transaction writes)
        conn.set_session(readonly=True, autocommit=True)
    else:
        # Allow writes; leave autocommit False so callers can control tx
        conn.set_session(readonly=False, autocommit=False)
    return conn

def _startup_db_probe() -> bool:
    """
    Try a tiny probe to confirm DB is reachable. Log success/failure.
    """
    try:
        with _db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                _ = cur.fetchone()
        logger.info("✅ PostgreSQL/Timescale connection successful (host=%s, db=%s, readonly=%s)",
                    DB_HOST, DB_NAME, not ENABLE_WRITE)
        return True
    except Exception as e:
        logger.warning("⚠️ PostgreSQL/Timescale connection failed: %s", e)
        return False

# Probe on startup
_startup_db_probe()

# -------------
# HA API helper
# -------------
def _headers():
    return {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}

# ------------
# MCP server
# ------------
mcp = FastMCP("ha-conversation-tools", version="0.1.0")

# ------------------------
# Tools: HA REST endpoints
# ------------------------
@mcp.tool()
def last_state(entity_id: str) -> Dict[str, Any]:
    logger.debug("last_state(entity_id=%s)", entity_id)
    url = f"{HA_URL}/api/states/{entity_id}"
    with httpx.Client(timeout=15) as s:
        r = s.get(url, headers=_headers())
        if r.status_code == 404:
            logger.warning("Entity not found: %s", entity_id)
            return {"ok": False, "error": f"Entity {entity_id} not found"}
        r.raise_for_status()
        data = r.json()
    return {
        "ok": True,
        "entity_id": entity_id,
        "state": data.get("state"),
        "attributes": data.get("attributes", {}),
        "last_changed": data.get("last_changed"),
    }

@mcp.tool()
def history_range(entity_id: str, start_iso: str, end_iso: str, no_attributes: bool = True) -> Dict[str, Any]:
    logger.debug(
        "history_range(entity_id=%s, start=%s, end=%s, no_attributes=%s)",
        entity_id, start_iso, end_iso, no_attributes
    )
    url = f"{HA_URL}/api/history/period/{start_iso}"
    params = {
        "filter_entity_id": entity_id,
        "end_time": end_iso,
        "no_attributes": str(no_attributes).lower(),
    }
    with httpx.Client(timeout=30) as s:
        r = s.get(url, headers=_headers(), params=params)
        r.raise_for_status()
        data = r.json()
    rows = data[0] if data else []
    return {"ok": True, "entity_id": entity_id, "rows": rows}

@mcp.tool()
def energy_sum(statistic_id: str, start_iso: str, end_iso: str, period: str = "hour") -> Dict[str, Any]:
    logger.debug(
        "energy_sum(statistic_id=%s, start=%s, end=%s, period=%s)",
        statistic_id, start_iso, end_iso, period
    )
    url = f"{HA_URL}/api/services/recorder/get_statistics"
    payload = {
        "start": start_iso,
        "end": end_iso,
        "period": period,
        "statistic_ids": [statistic_id],
    }
    with httpx.Client(timeout=30) as s:
        r = s.post(url, headers=_headers(), content=json.dumps(payload))
        r.raise_for_status()
        data = r.json()
    series: List[Dict[str, Any]] = data.get(statistic_id, [])
    total = 0.0
    for p in series:
        if isinstance(p, dict) and (v := p.get("sum")) is not None:
            try:
                total += float(v)
            except Exception:
                pass
    return {"ok": True, "statistic_id": statistic_id, "period": period, "total": total, "points": series}

# ----------------------------
# Tools: PostgreSQL (safe by default)
# ----------------------------
def _is_safe_select(sql: str) -> bool:
    """
    Very simple guard: allow only SELECT (after trimming comments/whitespace).
    Blocks UPDATE/DELETE/INSERT/DDL etc. Ignored if ENABLE_WRITE=True.
    """
    stripped = sql.lstrip()
    # Strip leading comments: /* ... */ and -- ...
    while True:
        if stripped.startswith("/*"):
            end = stripped.find("*/")
            if end == -1:
                return False
            stripped = stripped[end + 2 :].lstrip()
            continue
        if stripped.startswith("--"):
            nl = stripped.find("\n")
            if nl == -1:
                return False
            stripped = stripped[nl + 1 :].lstrip()
            continue
        break
    return stripped[:6].upper() == "SELECT"

@mcp.tool()
def sql_query(query: str, limit: int = 200, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run SQL against the recorder DB.
    - If ENABLE_WRITE=False: only SELECT is allowed (server-enforced) and connection is read-only.
    - If ENABLE_WRITE=True: any SQL is allowed; transaction control via autocommit=False.
    """
    logger.debug("sql_query(limit=%s) query=%s", limit, query)

    if not ENABLE_WRITE and not _is_safe_select(query):
        logger.warning("Rejected non-SELECT query (enable_write=False)")
        return {"ok": False, "error": "Only SELECT queries are allowed. Set enable_write=true to allow writes."}

    if limit <= 0:
        limit = 200

    try:
        with _db_connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if params and isinstance(params, dict):
                    cur.execute(query, params)
                else:
                    cur.execute(query)

                # If read-only/SELECT: fetch up to limit
                if not ENABLE_WRITE or _is_safe_select(query):
                    rows: List[Dict[str, Any]] = cur.fetchmany(size=limit)
                    logger.info("SQL returned %d row(s) (capped at %d)", len(rows), limit)
                    return {"ok": True, "rows": rows, "rowcount": len(rows)}
                else:
                    # Write or DDL — commit and return rowcount
                    conn.commit()
                    logger.info("SQL write/DDL executed (rowcount=%s)", cur.rowcount)
                    return {"ok": True, "rowcount": cur.rowcount}
    except Exception as e:
        logger.error("SQL query failed: %s", e)
        return {"ok": False, "error": str(e)}

@mcp.tool()
def db_status() -> Dict[str, Any]:
    """Simple status check for DB connectivity."""
    try:
        with _db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT NOW() AT TIME ZONE 'UTC' AS utc_now;")
                row = cur.fetchone()
        logger.info("db_status OK: %s", row)
        return {"ok": True, "detail": row, "enable_write": ENABLE_WRITE}
    except Exception as e:
        logger.warning("db_status FAILED: %s", e)
        return {"ok": False, "error": str(e), "enable_write": ENABLE_WRITE}

# --------------------------
# SSE transport / Starlette
# --------------------------
sse = SseServerTransport(mcp)
app = Starlette(routes=[Mount("/sse", app=sse.app)])
