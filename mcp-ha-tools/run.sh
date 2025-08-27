#!/bin/sh
set -eu

: "${HA_URL:=http://homeassistant:8123}"

# Read log level from options.json without heredoc (robust on BusyBox ash)
LOG_LEVEL="$(python3 -c 'import json,sys
try:
    with open("/data/options.json") as f:
        val = str(json.load(f).get("log_level","INFO")).upper()
        print(val if val in ["DEBUG","INFO","WARNING","ERROR","CRITICAL","NOTSET"] else "INFO")
except Exception:
    print("INFO")' )"

# Sanitize
LOG_LEVEL="$(printf "%s" "$LOG_LEVEL" | tr -d "" )"
LOG_LEVEL_LOWER="$(printf "%s" "$LOG_LEVEL" | tr "[:upper:]" "[:lower:]")"

echo "Starting MCP HA Tools Server ..."
echo "HA_URL=${HA_URL}"
echo "LOG_LEVEL=${LOG_LEVEL}"
echo "Python: $(python3 -V || true)"
echo "Uvicorn: $(uvicorn --version || true)"

export LOG_LEVEL
exec uvicorn --app-dir /app server:app --host 0.0.0.0 --port 8080 --log-level "$LOG_LEVEL_LOWER"
