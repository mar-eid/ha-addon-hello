#!/usr/bin/env bash
set -euo pipefail

# Default HA_URL hvis den ikke er eksportert fra miljøet
: "${HA_URL:=http://homeassistant:8123}"

# Les loggnivå fra /data/options.json (fallback INFO)
LOG_LEVEL="$(
python3 - <<'PY' 2>/dev/null || echo INFO
import json
try:
    with open('/data/options.json') as f:
        val = str(json.load(f).get('log_level','INFO')).upper()
        print(val if val in ['DEBUG','INFO','WARNING','ERROR','CRITICAL','NOTSET'] else 'INFO')
except Exception:
    print('INFO')
PY
)"

# Fjern eventuelle CR og whitespace som kan snike seg inn
LOG_LEVEL="$(printf '%s' "$LOG_LEVEL" | tr -d '\r' )"
LOG_LEVEL_LOWER="$(printf '%s' "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')"

echo "Starting MCP HA Tools Server ..."
echo "HA_URL=${HA_URL}"
echo "LOG_LEVEL=${LOG_LEVEL}"
echo "Python: $(python3 -V || true)"
echo "Uvicorn: $(uvicorn --version || true)"

export LOG_LEVEL
exec uvicorn server:app --host 0.0.0.0 --port 8080 --log-level "$LOG_LEVEL_LOWER"
