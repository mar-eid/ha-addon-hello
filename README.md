# MCP HA Tools Server (Add-on)

This add-on runs a local **Model Context Protocol (MCP) SSE server** for Home Assistant.  
It exposes tools the Conversation agent can call to read history, energy statistics, and run SQL against the recorder database (PostgreSQL/Timescale). A **write-safety toggle** prevents accidental writes by default.

## Features
- Tools:
  - `last_state(entity_id)`
  - `history_range(entity_id, start_iso, end_iso, no_attributes=True)`
  - `energy_sum(statistic_id, start_iso, end_iso, period="hour")`
  - `sql_query(query, limit=200, params=None)` (read-only unless `enable_write=true`)
  - `db_status()` (checks DB connectivity)
- Configurable log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, `NOTSET`
- **Write safety**: `enable_write=false` by default (read-only DB session + SELECT-only guard)
- Logs go to the Add-on log buffer (Supervisor → Add-on → Log)
- Automatic DB connection probe at startup

## Installation
1) Add this repository in Home Assistant:  
   **Settings → Add-ons → Add-on Store → ⋮ → Repositories** → paste your repo URL.  
2) Install **MCP HA Tools Server**.  
3) Configure (see below) and **Start**.

## Configuration
Open **Add-on → Configuration** and set:

```yaml
ha_url: "http://homeassistant:8123"
log_level: "INFO"

db_host: "core-postgres"
db_port: 5432
db_name: "homeassistant"
db_user: "ha_reader"
db_password: "CHANGE_ME"

# Safety toggle: default false (read-only connection + SELECT-only guard)
enable_write: false
```

### Database (PostgreSQL/Timescale) setup
Create a **read-only** user in PostgreSQL (recommended even if you enable writes only for maintenance):

```sql
CREATE ROLE ha_reader LOGIN PASSWORD 'CHANGE_ME';
GRANT CONNECT ON DATABASE homeassistant TO ha_reader;
GRANT USAGE ON SCHEMA public TO ha_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ha_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ha_reader;
```

> With `enable_write: false` the add-on opens a **read-only** connection and `sql_query` rejects any non-SELECT statements.  
> Setting `enable_write: true` opens a read-write session and allows updates/DDL; use only when you fully trust the tool call.

## Testing

### 1) Verify the SSE endpoint
Open:
```
http://homeassistant.local:8080/sse
```
An SSE stream should appear (connection stays open). If you see “connection refused”, the add-on isn’t running or the port is blocked.

### 2) Check logs
**Settings → Add-ons → MCP HA Tools Server → Log**  
- Success:
  ```
  ✅ PostgreSQL/Timescale connection successful (host=core-postgres, db=homeassistant, readonly=True)
  ```
- Failure:
  ```
  ⚠️ PostgreSQL/Timescale connection failed: ...
  ```

### 3) Check DB via tool
From an MCP client / Conversation:
```json
{ "tool": "db_status", "arguments": {} }
```

### 4) Example SQL
- Read-only (works with `enable_write=false`):
```json
{
  "tool": "sql_query",
  "arguments": {
    "query": "SELECT entity_id, state, last_updated_ts FROM states ORDER BY last_updated_ts DESC",
    "limit": 50
  }
}
```
- Write (requires `enable_write=true`):
```json
{
  "tool": "sql_query",
  "arguments": {
    "query": "CREATE TEMP TABLE demo(id int);"
  }
}
```

## Auto Update notes
- Bump `"version"` in `mcp-ha-tools/config.json` for each release (e.g., `0.1.5`).
- Push to your repo’s default branch.
- In Add-on Store click **⋮ → Reload** (or wait for Supervisor auto refresh).
- With **Auto update** enabled, Supervisor updates once it sees the new version.

## Troubleshooting
- If the add-on doesn’t appear or won’t update:
  - Ensure `repository.json` is in repo root and `mcp-ha-tools/` contains at least `config.json` + `Dockerfile`.
  - Reload repositories in Add-on Store (⋮ → Reload), then open the add-on page.
  - Check **Settings → System → Logs** and Supervisor logs for build errors.
- If pip install fails on Alpine (PEP 668):
  - Use a **virtualenv** and install Python packages there (the provided Dockerfile already does this).
