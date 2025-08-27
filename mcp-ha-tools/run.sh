#!/usr/bin/env bash
set -euo pipefail

# Read log level from /data/options.json (fallback INFO)
LOG_LEVEL="$(python - <<'PY' 2>/dev/null || echo INFO)
import json
try:
    with open('/data/options.json') as f:
        val = str(json.load(f).get('log_level','INFO')).upper()
        print(val if val in ['DEBUG','INFO','WARNING','ERROR','CRITICAL','NOTSET'] else 'INFO')
except Exception:
    print('INFO')
PY
)"

echo "Starting MCP HA Tools Server ..."
echo "HA_URL=${HA_URL}"
echo "LOG_LEVEL=${LOG_LEVEL}"

export LOG_LEVEL
exec uvicorn server:app --host 0.0.0.0 --port 8080 --log-level "$(echo "${LOG_LEVEL}" | tr '[:upper:]' '[:lower:]')"


echo "Python: $(python -V)"
echo "Uvicorn: $(uvicorn --version || true)"

export LOG_LEVEL
exec uvicorn server:app --host 0.0.0.0 --port 8080 --log-level "$(echo "${LOG_LEVEL}" | tr '[:upper:]' '[:lower:]')"