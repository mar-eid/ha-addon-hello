# Changelog

## 0.1.7
- Fixed critical startup issues in `run.sh` and `Dockerfile`:
  - Replaced HEREDOC with a Python one-liner to avoid `unterminated here-document` warnings.
  - Added safe default for `HA_URL` so `set -u` no longer crashes if unset.
  - Cleaned log-level parsing to avoid stray CR/LF causing `--log-level 'info\n)'` errors.
  - Updated Dockerfile with `WORKDIR /app` so `uvicorn` can import `server.py`.
  - Normalized `run.sh` line endings and ensured it executes with `uvicorn --app-dir /app server:app`.
- These fixes resolve:
  - `HA_URL: unbound variable`
  - `Invalid value for '--log-level': 'info\n)'`
  - `Error loading ASGI app. Could not import module "server"`.
- Version bump to 0.1.7.

## 0.1.6
- Config update: `ha_url` now properly comes from `options` and is exported as `HA_URL`.
- This allows the add-on user to configure Home Assistant URL directly in the UI.
- Version bump to 0.1.6.

## 0.1.5
- Added new configuration toggle `enable_write` (default: false).
  - When false: DB connection is opened in read-only mode and `sql_query` enforces SELECT-only.
  - When true: DB connection allows write/DDL operations (use with caution).
- Environment variable `ENABLE_WRITE` is exported from config.
- Extended logging: startup log now shows whether write mode is enabled.
- Updated README with:
  - Detailed configuration instructions for SQL connection.
  - Example using PostgreSQL/Timescale URI.
  - Clear explanation of write-safety toggle.
- Version bump to 0.1.5.

## 0.1.4
- Added full support for standard Home Assistant log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, `NOTSET`).
- Added PostgreSQL/TimescaleDB connection options (`db_host`, `db_port`, `db_name`, `db_user`, `db_password`).
- Implemented automatic DB connection probe at startup with log output (✅ or ⚠️).
- New tool: `sql_query(query, limit=200)` for read-only SELECT queries against the recorder DB.
- New tool: `db_status()` to check DB connectivity and return current UTC timestamp.
- Extended logging in `server.py` (tool calls, DB connection success/failure).
- Updated README.md with testing instructions, including browser check via `http://homeassistant.local:8080/sse`.

## 0.1.3
- Internal build (not released).
- Added improved logging and environment variable handling.

## 0.1.2
- Internal build (not released).
- Basic log level configuration added.

## 0.1.1
- Added initial logging support, configurable log level.
- Minor fixes for add-on startup.

## 0.1.0
- Initial version of the MCP HA Tools Server add-on.
- Provided tools: `last_state`, `history_range`, `energy_sum`.
- SSE endpoint for MCP client integration.
