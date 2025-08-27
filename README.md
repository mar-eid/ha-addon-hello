# MCP HA Tools Server (Add-on)

This add-on runs a local **Model Context Protocol (MCP) SSE server** for Home Assistant.
It exposes tools for the Conversation agent to read state history, energy statistics, and run SQL (read-only by default).

- Tools: `last_state`, `history_range`, `energy_sum`, `sql_query`, `db_status`
- **Write safety**: `enable_write: false` by default (SELECT-only + read-only session)
- API access is optional: Supervisor token (recommended) or paste a Long-Lived Access Token into `ha_token`.

## Quick start
1. Add this repository in Home Assistant Add-on Store.
2. Open the add-on → **Configuration** and set:
   ```yaml
   ha_url: "http://homeassistant.local:8123"
   ha_token: ""            # optional LLAT; leave empty if using Supervisor token
   log_level: "INFO"
   db_host: "core-postgres"
   db_port: 5432
   db_name: "homeassistant"
   db_user: "ha_reader"
   db_password: "CHANGE_ME"
   enable_write: false
   ```
3. Start the add-on. Visit `http://homeassistant.local:8080/sse` to verify SSE.
4. Check add-on **Log** for DB probe (✅ / ⚠️).

## Example tools
- DB status:
  ```json
  { "tool": "db_status", "arguments": {} }
  ```
- SQL (read-only):
  ```json
  { "tool": "sql_query",
    "arguments": { "query": "SELECT NOW() AT TIME ZONE 'UTC' AS utc_now" }
  }
  ```
