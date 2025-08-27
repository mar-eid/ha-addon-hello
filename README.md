# MCP HA Tools Server (Add-on)

This repository provides a Home Assistant add-on that runs a local **Model Context Protocol (MCP) SSE server**.  
It exposes tools for the Home Assistant Conversation agent, giving LLMs read-only access to state history, energy statistics, and direct SQL queries (PostgreSQL/Timescale).

## Features
- Tools available to Conversation:
  - `last_state(entity_id)`
  - `history_range(entity_id, start_iso, end_iso, no_attributes=True)`
  - `energy_sum(statistic_id, start_iso, end_iso, period="hour")`
  - `sql_query(query, limit=200)` (read-only, SELECT only)
  - `db_status()` (check DB connection)
- Configurable log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, `NOTSET`).
- Logs written to Home Assistant add-on log buffer (view in Supervisor UI).
- Automatic DB connection check at startup.

## Installation
1. Add this repository to Home Assistant:  
   **Settings → Add-ons → Add-on Store → ⋮ → Repositories**  
   Paste the repo URL:  
https://github.com/mar-eid/ha-addon-hello

markdown
Kopier kode

2. Find and install **MCP HA Tools Server**.

3. Configure the add-on under **Configuration**:
- `ha_url` (default: `http://homeassistant:8123`)
- `log_level` (default: `INFO`)
- `db_host`, `db_port`, `db_name`, `db_user`, `db_password` for PostgreSQL/Timescale.

4. Start the add-on.

## Testing the Add-on

### 1. Verify the SSE endpoint
Open a browser and go to:

http://homeassistant.local:8080/sse

sql
Kopier kode

- If the add-on is running, you should see an SSE stream start (connection stays open).
- If you see “connection refused”, the add-on is not running or the port is blocked.

### 2. Check the logs in Home Assistant
Go to:  
**Settings → Add-ons → MCP HA Tools Server → Log**

- On successful DB connection, you will see:
✅ PostgreSQL/Timescale connection successful (host=core-postgres, db=homeassistant)

diff
Kopier kode
- If something failed, you’ll see:
⚠️ PostgreSQL/Timescale connection failed: ...

mathematica
Kopier kode

### 3. Check DB connectivity via `db_status`
If you have the MCP Client integration enabled in HA:
- Ask your Conversation agent:  
> “Call db_status tool”
- Or run from an MCP client:
```json
{
  "tool": "db_status",
  "arguments": {}
}
You should get back a JSON object with the current UTC time reported from the database.

Development Notes
PostgreSQL access is enforced as read-only (connection is opened with readonly=True and autocommit).

sql_query rejects any non-SELECT statements for safety.

Default DB settings assume HA’s community Postgres add-on with a read-only user.

Remember to bump version in config.json and update CHANGELOG.md on every release.