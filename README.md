# MCP HA Tools Add‑on

This repository contains a Home Assistant add‑on that exposes local **Model Context Protocol (MCP)** tools to the Conversation agent in Home Assistant. It allows your voice assistant to call custom tools such as `last_state`, `history_range` and `energy_sum` to access data from your Home Assistant instance without relying on external services.

## Repository structure

The repo consists of two parts:

| Path | Description |
| --- | --- |
| `repository.json` | Metadata describing this add‑on repository for Home Assistant. |
| `mcp‑ha‑tools/` | The add‑on itself, including its configuration, Dockerfile and runtime scripts. |

## Add‑on details

When the add‑on starts it launches a small SSE server on port **8080** that registers several MCP tools for Home Assistant's Conversation agent. These tools provide safe, read‑only access to state history and energy statistics via Home Assistant’s REST API. You can install this repository in the **Add‑on Store** and enable the add‑on via the MCP Client integration.

### Auto update

Home Assistant supports automatic updates for add‑ons through the Supervisor. To make use of this feature:

1. Increment the `version` field in `mcp‑ha‑tools/config.json` whenever you make changes to the add‑on code.
2. Commit and push the updated files to your GitHub repository.
3. In Home Assistant, enable **Auto update** for the installed add‑on. The Supervisor will periodically check your repository and automatically download new versions when they become available.

## Installing

Follow these steps to install the MCP tools add‑on:

1. Push this repository to GitHub at the URL specified in `repository.json`. Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username before pushing.
2. In Home Assistant, navigate to **Settings → Add‑ons → Add‑on Store**.
3. Click the menu (⋮) → **Repositories** and add the GitHub URL of this repository.
4. Refresh the page; you should see the **MCP HA Tools Server** listed in the Add‑on Store.
5. Install and start the add‑on.
6. Add the MCP client integration via **Settings → Integrations** and provide the SSE endpoint `http://homeassistant:8080/sse` (or similar) from the add‑on when prompted. This enables the Conversation agent to discover and call your custom tools.

## Contributing

Feel free to extend the add‑on by adding additional MCP tools or improving the documentation. Remember to bump the `version` in `config.json` when you change behaviour, and ensure all text remains in English so it is easy for others to understand.
