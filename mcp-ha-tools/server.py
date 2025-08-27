"""
MCP HA Tools Server
====================

This module implements a simple SSE server using the Model Context Protocol (MCP) Python
SDK. The server defines a handful of tools that can be consumed by the Home Assistant
Conversation agent via the MCP client integration. These tools allow read‑only access
to entity state history and energy statistics from your Home Assistant instance.

Tools exposed:

* `last_state(entity_id)`: Return the most recent state object for an entity.
* `history_range(entity_id, start_iso, end_iso, no_attributes=True)`: Return state
  history between two ISO timestamps.
* `energy_sum(statistic_id, start_iso, end_iso, period="hour")`: Summarise energy
  consumption over a period using Home Assistant's statistics service.

The server expects two environment variables set by Home Assistant:
```
HA_URL   – the base URL of the Home Assistant instance (default http://homeassistant:8123)
HA_TOKEN – a long‑lived access token or supervisor token for API authentication
```
The SSE endpoint is exposed under `/sse` and should be registered in the MCP client
integration. See README.md for installation instructions.
"""

import json
import os
from typing import Any, Dict, List

import httpx
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

# Obtain configuration from environment. When running as an add‑on, HA_URL and HA_TOKEN
# are injected by Home Assistant via config.json (see that file for defaults). If not
# provided, fallback to reasonable defaults.
HA_URL: str = os.environ.get("HA_URL", "http://homeassistant:8123")
HA_TOKEN: str = os.environ.get("HA_TOKEN", "")

# Initialise the MCP server. The name should be unique to your add‑on.
mcp = FastMCP("ha-conversation-tools")


@mcp.tool()
def last_state(entity_id: str) -> Dict[str, Any]:
    """Return the most recent state for the given entity.

    Parameters
    ----------
    entity_id: str
        The full entity ID (e.g., "sensor.living_room_temperature").

    Returns
    -------
    dict
        A JSON object representing the state of the entity. If the entity does not
        exist, an HTTP error will be raised upstream.
    """
    headers = {"Authorization": f"Bearer {HA_TOKEN}"}
    url = f"{HA_URL}/api/states/{entity_id}"
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def history_range(entity_id: str, start_iso: str, end_iso: str, no_attributes: bool = True) -> Dict[str, Any]:
    """Return state history for an entity between two ISO timestamps.

    Parameters
    ----------
    entity_id: str
        The entity ID to query.
    start_iso: str
        ISO8601 timestamp (UTC) marking the beginning of the interval.
    end_iso: str
        ISO8601 timestamp (UTC) marking the end of the interval.
    no_attributes: bool, optional
        If true, omit attribute data from the returned states to reduce payload size.

    Returns
    -------
    dict
        A dictionary containing the entity ID and a list of state objects for the
        requested interval.
    """
    headers = {"Authorization": f"Bearer {HA_TOKEN}"}
    url = f"{HA_URL}/api/history/period/{start_iso}"
    params = {
        "filter_entity_id": entity_id,
        "end_time": end_iso,
        "no_attributes": str(no_attributes).lower(),
    }
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
    rows = result[0] if result else []
    return {"entity_id": entity_id, "rows": rows}


@mcp.tool()
def energy_sum(statistic_id: str, start_iso: str, end_iso: str, period: str = "hour") -> Dict[str, Any]:
    """Summarise energy consumption for a statistic over a period.

    This tool calls the `recorder.get_statistics` service to obtain aggregated energy
    statistics for the specified sensor or meter and then sums the `sum` values
    returned by the API.

    Parameters
    ----------
    statistic_id: str
        The statistic ID (e.g., a sensor entity ID that records energy usage).
    start_iso: str
        Start of the period as an ISO8601 timestamp (UTC).
    end_iso: str
        End of the period as an ISO8601 timestamp (UTC).
    period: str, optional
        Aggregation period recognised by Home Assistant (e.g., "hour", "day").

    Returns
    -------
    dict
        A dictionary containing the statistic ID, period, total energy sum and
        the raw series data.
    """
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "start": start_iso,
        "end": end_iso,
        "period": period,
        "statistic_ids": [statistic_id],
    }
    url = f"{HA_URL}/api/services/recorder/get_statistics"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, content=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
    series: List[Dict[str, Any]] = result.get(statistic_id, [])
    total = sum(point.get("sum", 0) for point in series if isinstance(point, dict))
    return {
        "statistic_id": statistic_id,
        "period": period,
        "total": total,
        "points": series,
    }


# Build the Starlette application to serve the SSE endpoint. Home Assistant's MCP
# client integration will poll this endpoint to discover available tools.
sse = SseServerTransport(mcp)
app = Starlette(routes=[Mount("/sse", app=sse.app)])