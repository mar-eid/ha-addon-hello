import os
import json
import logging
from typing import Dict, Any, List

import httpx
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

HA_URL = os.environ.get("HA_URL", "http://homeassistant:8123").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

if not HA_TOKEN:
    raise RuntimeError("HA_TOKEN (Supervisor or Long-Lived Token) is required.")

mcp = FastMCP("ha-conversation-tools", version="0.1.0")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("mcp-ha-tools")
logger.info("Starting MCP HA Tools Server (log_level=%s, ha_url=%s)", LOG_LEVEL, HA_URL)

def _headers():
    return {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}

@mcp.tool()
def last_state(entity_id: str) -> Dict[str, Any]:
    """Return last known state via /api/states/<entity_id>."""
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
    """Return history via /api/history/period/<start_iso> with ?end_time=<end_iso>."""
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
    """Sum energy from recorder.get_statistics for a statistic_id (e.g., energy)."""
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

# SSE transport for MCP client
sse = SseServerTransport(mcp)
app = Starlette(routes=[Mount("/sse", app=sse.app)])
