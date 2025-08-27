#!/usr/bin/env bash
set -euo pipefail

# Entry point script for the MCP HA Tools add‑on. It launches the FastMCP SSE server
# implemented in server.py via Uvicorn. Environment variables HA_URL and HA_TOKEN
# are provided by Home Assistant when running as an add‑on.

exec uvicorn server:app --host 0.0.0.0 --port 8080