---
agent: opencode run
commands:
  - name: tests
    run: uv run pytest -v --tb=short 2>&1
    timeout: 120
  - name: lint
    run: uv run ruff check . 2>&1
    timeout: 60
  - name: format
    run: uv run ruff format --check . 2>&1
    timeout: 60
  - name: git-log
    run: git log --oneline -5 2>&1
    timeout: 30
args: {}
credit: false
---

# Chatvolt MCP - Autonomous Improvement Loop

You are working on the **Chatvolt MCP Server** - an MCP (Model Context Protocol) server for the Chatvolt AI platform.

## Project Structure

Python 3.13 project using `uv` for dependency management. Starlette-based server with Streamable HTTP transport at `/sse` (backward-compatible path).

Key files:
- `src/server.py` - Main MCP server (tools, prompts, resources, completions handlers)
- `src/tools/loader.py` - Tool registry that maps Chatvolt API endpoints to MCP tools
- `src/tools/definitions/` - Individual tool definition modules (agents, crm, conversations, artifacts, datastores, contacts, dispatches, blacklist)
- `src/prompts/workflows.py` - Pre-defined workflow prompts
- `src/config.py` - Environment configuration
- `tests/` - pytest test suite

## Current State

### Git Log
{{ commands.git-log }}

### Test Results
{{ commands.tests }}

### Lint Results
{{ commands.lint }}

### Format Check
{{ commands.format }}

## Instructions

### Phase 1: Fix Issues (if any)
1. **If tests are failing, fix them first.** Read the test output, understand the failure, and make targeted fixes.
2. **If lint has errors, fix them next.** Run `uv run ruff check --fix .` to auto-fix what's possible.
3. **If formatting is off, fix it.** Run `uv run ruff format .` to auto-format.
4. **After fixes, commit your changes** with a clear conventional commit message.

### Phase 2: Work Through TODO.md
1. Read `TODO.md` and find the first unchecked item.
2. Implement it completely with tests.
3. Check off the item in `TODO.md`.
4. Commit with a message describing the change.

### Phase 3: Autonomous Improvement (when TODO.md is complete)
When all TODO items are checked, proactively improve the server:

1. **Fetch Chatvolt API docs**: Read https://docs.chatvolt.ai/ and its sub-pages to discover new features, endpoints, or capabilities that aren't yet implemented as MCP tools/resources/prompts.
2. **Fetch MCP spec**: Read https://modelcontextprotocol.io/ to discover new MCP capabilities (resources, completions, notifications, structured content, etc.) that could enhance this server.
3. **Implement missing features**: Add new tools, resources, prompts, or improve existing ones based on what you find.
4. **Add comprehensive tests**: Every new feature must have tests. Target 100% coverage.
5. **Update documentation**: Keep README.md and TODO.md in sync with changes.
6. **Commit each logical change separately** with descriptive messages.

## Guardrails

<!-- Read guardrails.md for persistent rules learned from past iterations -->
{{ ralph.guardrails }}
