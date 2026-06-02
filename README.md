# Chatvolt MCP Server

An MCP (Model Context Protocol) server for Chatvolt AI, providing tools, resources, prompts, and completions for managing agents, contacts, conversations, CRM workflows, and more.

## Features

- **Streamable HTTP Transport**: Runs over HTTP with JSON-RPC (no SSE, no WebSockets).
- **81 Tools**: Comprehensive coverage of Chatvolt API endpoints.
- **Tool Annotations**: Every tool has `readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint` annotations for safe AI execution.
- **Dynamic Tool Discovery**: Automatically maps Chatvolt OpenAPI specifications to MCP tools.
- **8 Workflow Prompts**: Pre-defined guided workflows for common tasks.
- **Resources**: Access agent configs, tools, and prompts as MCP resources.
- **Completions**: Auto-suggest for model names, statuses, channels, and more.
- **Structured Errors**: All errors return JSON `{error, status, message}` for easy parsing.
- **Python-based**: Built with Python and `uv`.

## Installation

1. **Install uv**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and Initialize**:
   ```bash
   cd chatvolt-mcp
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your CHATVOLT_API_KEY
   ```

## Running the Server

```bash
uv run python run.py
```
The server will start at `http://localhost:8000`.

## Usage with MCP Clients

### VS Code / GitHub Copilot

Add the following to your VS Code MCP settings (`.vscode/mcp.json` or user settings):

```json
{
  "servers": {
    "MCP_Chatvolt": {
      "url": "http://localhost:8000/sse",
      "type": "http"
    }
  }
}
```

### Any MCP Client (Claude Desktop, Cursor, VS Code, OpenCode)

Point your MCP client to the Streamable HTTP endpoint:
- **URL**: `http://localhost:8000/mcp`
- **Type**: `http` (Streamable HTTP)

## Usage with OpenCode

1. **Start the Chatvolt MCP server**:
   ```bash
   uv run python run.py
   ```

2. **Configure OpenCode**:
   Add the following to your `opencode.jsonc` (create it in your project root if it doesn't exist):
   ```jsonc
   {
     "$schema": "https://opencode.ai/config.json",
     "mcp": {
       "chatvolt": {
         "type": "remote",
         "url": "http://localhost:8000/sse",
         "enabled": true
       }
     }
   }
   ```

3. **Start OpenCode**:
   ```bash
   opencode
   ```

   The Chatvolt MCP tools will now be available in your OpenCode sessions.

## Available Tools (81 total)

### Agents
- `query_agent` - Query an agent with a message
- `get_agent` - Get agent details
- `create_agent` - Create a new agent
- `update_agent` - Update agent configuration
- `delete_agent` - Delete an agent
- `get_models` - List available AI models
- `toggle_webhook` - Enable/disable webhooks
- `get_agent_tools` - List agent tools
- `create_agent_tool` - Create a tool for an agent
- `update_agent_tool` - Update agent tool
- `delete_agent_tool` - Delete agent tool

### Conversations
- `list_conversations` - List conversations
- `get_conversation` - Get conversation details
- `get_conversation_messages` - Get conversation messages
- `get_message` - Get single message
- `set_conversation_ai` - Toggle AI for conversation
- `register_message_in_context` - Register message without sending
- `create_conversation` - Create new conversation
- `resolve_conversation` - Mark as resolved
- `delete_conversation` - Delete conversation
- `request_human_intervention` - Request human handoff

### Contacts
- `list_contacts` - List contacts
- `get_contact` - Get contact details
- `create_contact` - Create contact
- `update_contact` - Update contact
- `delete_contact` - Delete contact
- `get_contact_conversations` - Get contact's conversations

### Dispatches
- `list_dispatches` - List dispatch campaigns
- `get_dispatch` - Get dispatch details
- `create_dispatch` - Create dispatch campaign
- `update_dispatch` - Update dispatch
- `delete_dispatch` - Delete dispatch

### Artifacts
- `search_artifacts` - Search artifacts
- `list_artifacts` - List artifacts
- `get_artifact` - Get artifact details
- `create_artifact` - Create artifact
- `update_artifact` - Update artifact
- `delete_artifact` - Delete artifact
- `list_artifact_media` - List artifact media
- `upload_artifact_media` - Upload media
- `update_artifact_media` - Update media
- `delete_artifact_media` - Delete media
- `list_artifact_categories` - List categories
- `create_artifact_category` - Create category
- `get_artifact_category` - Get category
- `update_artifact_category` - Update category
- `delete_artifact_category` - Delete category

### Datastores & Datasources
- `list_datastores` - List datastores
- `get_datastore` - Get datastore
- `create_datastore` - Create datastore
- `update_datastore` - Update datastore
- `delete_datastore` - Delete datastore
- `query_datastore` - Query datastore
- `list_datasources` - List datasources
- `get_datasource` - Get datasource
- `create_datasource` - Create datasource
- `update_datasource` - Update datasource
- `delete_datasource` - Delete datasource
- `sync_datasource` - Trigger sync
- `get_datasource_status` - Get sync status

### CRM (Flux CRM)
- `list_crm_scenarios` - List CRM scenarios
- `create_crm_scenario` - Create scenario
- `get_crm_scenario` - Get scenario
- `update_crm_scenario` - Update scenario
- `delete_crm_scenario` - Delete scenario
- `list_crm_steps` - List CRM steps
- `create_crm_step` - Create step
- `update_crm_step` - Update step
- `delete_crm_step` - Delete step
- `add_conversation_to_step` - Add conversation to step
- `move_conversation_to_step` - Move conversation
- `list_crm_logs` - List CRM logs
- `get_crm_log` - Get CRM log

### Z-API (WhatsApp)
- `zapi_list_instances` - List Z-API instances
- `zapi_send_text` - Send text message
- `zapi_send_media` - Send media message
- `zapi_send_template` - Send template
- `zapi_send_list` - Send list message
- `zapi_send_buttons` - Send buttons message

### Agent Blacklist
- `list_blacklist` - List blacklisted users
- `add_to_blacklist` - Add user to blacklist
- `remove_from_blacklist` - Remove from blacklist

## Available Prompts (8 total)

- `onboard_new_user` - Create contact and send welcome message
- `broadcast_campaign` - Set up dispatch campaign
- `create_new_agent` - Design and deploy new AI agent
- `setup_datastore` - Create datastore and ingest data
- `create_crm_workflow` - Build CRM scenarios and steps
- `whatsapp_outreach` - Send WhatsApp messages via Z-API
- `contact_enrichment` - Look up and manage contacts
- `agent_health_check` - Check agent status and conversations

## Available Resources

- `chatvolt://models` - Available AI models info
- `chatvolt://tools` - Complete tool catalog
- `chatvolt://prompts` - Available prompts
- `chatvolt://agent/{agentId}` - Agent configuration template

## Ralph Loop (Autonomous Development)

The project includes a Ralph Loop setup for autonomous code improvement.

```bash
# Run until all checks pass
./ralph-loop.sh

# Run exactly 5 iterations
./ralph-loop.sh -n 5

# Dry run (see prompt without executing)
./ralph-loop.sh --dry-run
```

The loop:
1. Runs tests and linting
2. Feeds results to opencode
3. opencode fixes issues and commits
4. Repeats until all checks pass
5. When idle, fetches docs to find improvements

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest -v

# Run linting
uv run ruff check .

# Auto-fix lint
uv run ruff check --fix .

# Format code
uv run ruff format .
```

## Project Structure

```
src/
├── server.py              # MCP server with tools, prompts, resources, completions
├── config.py             # Environment configuration
├── tools/
│   ├── loader.py         # Tool registry with annotations
│   ├── all_definitions.py
│   └── definitions/      # Tool definition modules
│       ├── agents.py
│       ├── conversations.py
│       ├── contacts.py
│       ├── dispatches.py
│       ├── artifacts.py
│       ├── datastores.py
│       ├── datasources.py
│       ├── crm.py
│       ├── crm_scenarios.py
│       ├── crm_logs.py
│       ├── blacklist.py
│       ├── zapi.py
│       └── conversation_mgmt.py
└── prompts/
    └── workflows.py      # Workflow prompts
tests/
├── test_server.py
├── test_loader.py
└── test_new_features.py
ralph/
├── RALPH.md              # Loop prompt
└── .ralph/
    └── guardrails.md    # Persistent memory
ralph-loop.sh             # Loop runner script
TODO.md                  # Task tracking
```
