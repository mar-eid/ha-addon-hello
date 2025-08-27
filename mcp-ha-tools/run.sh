#!/bin/sh
set -eu

# Default HA_URL dersom den ikke er eksportert
: "${HA_URL:=http://homeassistant.local:8123}"

# Les loggnivå fra /data/options.json (fallback INFO), og valider mot kjente nivåer
LOG_LEVEL="$(python3 -c 'import json,sys
try:
    with open("/data/options.json") as f:
        val = str(json.load(f).get("log_level","INFO")).upper()
        print(val if val in ["DEBUG","INFO","WARNING","ERROR","CRITICAL","NOTSET"] else "INFO")
except Exception:
    print("INFO")'
)"

# Trim CR og whitespace
LOG_LEVEL="$(printf "%s" "$LOG_LEVEL" | tr -d "\r" )"
LOG_LEVEL_LOWER="$(printf "%s" "$LOG_LEVEL" | tr "[:upper:]" "[:lower:]")"

echo "Starting MCP HA Tools Server ..."
echo "HA_URL=${HA_URL}"
echo "LOG_LEVEL=${LOG_LEVEL}"
echo "Python: $(python3 -V || true)"
echo "Uvicorn: $(uvicorn --version || true)"

export LOG_LEVEL
# Viktig: bruk --app-dir /app slik at 'server' kan importeres
exec uvicorn --app-dir /app server:app --host 0.0.0.0 --port 8080 --log-level "$LOG_LEVEL_LOWER"
