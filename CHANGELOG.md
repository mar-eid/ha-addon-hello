# Changelog

## 0.1.4
- Added full support for standard Home Assistant log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, `NOTSET`).
- Added PostgreSQL/TimescaleDB connection options (`db_host`, `db_port`, `db_name`, `db_user`, `db_password`).
- Implemented automatic DB connection probe at startup with log output (✅ or ⚠️).
- New tool: `sql_query(query, limit=200)` for read-only SELECT queries against the recorder DB.
- New tool: `db_status()` to check DB connectivity and return current UTC timestamp.
- Extended logging in `server.py` (tool calls, DB connection success/failure).
- Updated `README.md` with testing instructions, including browser check via `http://homeassistant.local:8080/sse`.

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
