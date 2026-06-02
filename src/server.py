import contextlib
import logging
from collections.abc import AsyncIterator

import mcp.types as types
from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

from src.config import set_request_auth_token
from src.prompts.workflows import PROMPTS, get_prompt_message
from src.tools.definitions import TOOLS_DEFINITION
from src.tools.loader import registry

logger = logging.getLogger("chatvolt-mcp")

app = Server(
    "chatvolt-mcp",
    version="1.0.0",
    instructions="MCP server for Chatvolt AI platform. Provides tools for managing agents, conversations, contacts, dispatches, and more.",
)


LOG_LEVELS = {"debug", "info", "notice", "warning", "error", "critical", "alert", "emergency"}

LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "notice": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    "alert": logging.CRITICAL,
    "emergency": logging.CRITICAL,
}


@app.set_logging_level()
async def handle_set_logging_level(level: str) -> types.EmptyResult:
    """Handle logging level setting requests."""
    if level not in LOG_LEVELS:
        raise ValueError(f"Invalid log level: {level}. Must be one of: {', '.join(LOG_LEVELS)}")
    logger.setLevel(LOG_LEVEL_MAP[level])
    for handler in logger.handlers:
        handler.setLevel(LOG_LEVEL_MAP[level])
    return types.EmptyResult()


async def send_log(level: str, data: dict | None = None, logger_name: str | None = None) -> None:
    """Send a log message notification to the client."""
    try:
        notification = types.LoggingMessageNotification(level=level, logger=logger_name, data=data)
        await app.request_context.session.send_notification(notification)
    except Exception:
        pass


def log_message(level: str, message: str, data: dict | None = None) -> None:
    """Log a message both to Python logger and via MCP notification."""
    getattr(logger, level.lower())(message)
    import asyncio

    with contextlib.suppress(RuntimeError):
        asyncio.create_task(send_log(level, {"message": message, **(data or {})}))


# --- Resources ---

RESOURCES = {
    "chatvolt://models": types.Resource(
        uri="chatvolt://models",
        name="Available LLM Models",
        description="List of all available AI models and their pricing",
        mimeType="application/json",
    ),
    "chatvolt://tools": types.Resource(
        uri="chatvolt://tools",
        name="All MCP Tools",
        description="Complete list of all available MCP tools with their schemas",
        mimeType="application/json",
    ),
    "chatvolt://prompts": types.Resource(
        uri="chatvolt://prompts",
        name="All Workflow Prompts",
        description="Complete list of all available workflow prompts with their arguments",
        mimeType="application/json",
    ),
    "chatvolt://voltapi-guide": types.Resource(
        uri="chatvolt://voltapi-guide",
        name="VoltAPI Script Writing Guide",
        description="Complete reference for writing VoltAPI sandboxed JavaScript functions — available globals, limitations, best practices, and examples.",
        mimeType="text/markdown",
    ),
}


@app.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources."""
    return list(RESOURCES.values())


@app.read_resource()
async def handle_read_resource(uri: str) -> str | bytes:
    """Read a specific resource by URI."""
    import json

    if uri == "chatvolt://models":
        return json.dumps({"note": "Use the get_models tool to retrieve available models and pricing"})
    elif uri == "chatvolt://tools":
        tools_info = {}
        for name, info in TOOLS_DEFINITION.items():
            tools_info[name] = {
                "method": info["method"],
                "path": info["path"],
                "description": info["description"],
                "parameters": info["input_schema"],
            }
        return json.dumps(tools_info, indent=2)
    elif uri == "chatvolt://prompts":
        prompts_info = {}
        for name, prompt in PROMPTS.items():
            prompts_info[name] = {
                "description": prompt.description,
                "arguments": [
                    {"name": a.name, "description": a.description, "required": a.required}
                    for a in (prompt.arguments or [])
                ],
            }
        return json.dumps(prompts_info, indent=2)
    elif uri == "chatvolt://voltapi-guide":
        return """# VoltAPI — Guia de Escrita de Scripts\n\n""
        "## Estrutura Básica\n\n"
        "Todo script deve ser uma função assíncrona que recebe `input` e retorna um valor:\n\n"
        "```javascript\n"
        "async (input) => {\n"
        "  // seu código aqui\n"
        "  return { resultado: \"ok\" };\n"
        "};\n"
        "```\n\n"
        "## Ambiente de Execução\n\n"
        "O código roda em um V8 isolate isolado (`isolated-vm`) com:\n\n"
        "| Recurso | Disponível? |\n"
        "|---|---|\n"
        "| `input` | ✅ O payload enviado |\n"
        "| `console.log / .error / .warn / .info` | ✅ Logs capturados e retornados |\n"
        "| `fetch(url, options)` | ✅ Com proteção SSRF |\n"
        "| `voltApi.get(url)` | ✅ GET autenticado para o Chatvolt |\n"
        "| `voltApi.post(url, body)` | ✅ POST autenticado para o Chatvolt |\n"
        "| `async / await` | ✅ |\n"
        "| `Promise` | ✅ |\n"
        "| `JSON.stringify / parse` | ✅ |\n"
        "| `Math`, `Date`, `RegExp`, `Array`, `Object`, `Map`, `Set` | ✅ |\n"
        "| `require()` | ❌ Bloqueado |\n"
        "| `import / export` | ❌ Bloqueado |\n"
        "| `fs`, `path`, `process`, `child_process` | ❌ Bloqueado |\n"
        "| `setTimeout`, `setInterval` | ❌ Bloqueado |\n"
        "| Acesso a IPs privados | ❌ Bloqueado pelo SSRF |\n\n"
        "## Globais Disponíveis\n\n"
        "### `input`\n"
        "O payload da requisição de execução.\n\n"
        "### `console`\n"
        "Os logs são capturados e retornados na resposta de execução no array `logs`.\n\n"
        "### `fetch(url, options)`\n"
        "Fetch padrão com proteção SSRF — não acessa IPs privados/internos.\n\n"
        "### `voltApi.get(url)`\n"
        "GET com Authorization já incluso para APIs internas do Chatvolt.\n\n"
        "### `voltApi.post(url, body)`\n"
        "POST com Authorization + Content-Type já inclusos para APIs internas.\n\n"
        "## Limitações\n\n"
        "- Timeout: 10s na VM, 60s no polling\n"
        "- Memória: 128MB por execução\n"
        "- Sem módulos Node.js\n"
        "- Sem setTimeout/setInterval\n\n"
        "## Boas Práticas\n\n"
        "1. Valide o input sempre\n"
        "2. Trate erros com try/catch\n"
        "3. Use console.log para debugar\n"
        "4. Prefira retornar objetos estruturados\n"
        "5. Evite loops infinitos ou operações pesadas (limite de 10s)\n"
        """
    elif uri.startswith("chatvolt://voltapi/"):
        import json
        function_name = uri.removeprefix("chatvolt://voltapi/")
        # Delegate to voltapi_get_function via the tool registry
        result = await registry.call_tool("voltapi_get_function", {"name": function_name})
        text = result[0].text if result else json.dumps({"error": "Function not found"})
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, indent=2)
        except (json.JSONDecodeError, TypeError):
            return text
    else:
        raise ValueError(f"Unknown resource: {uri}")


@app.list_resource_templates()
async def handle_list_resource_templates() -> list[types.ResourceTemplate]:
    """List resource templates."""
    return [
        types.ResourceTemplate(
            uriTemplate="chatvolt://agent/{agentId}",
            name="Agent Configuration",
            description="Get the configuration of a specific agent",
            mimeType="application/json",
        ),
        types.ResourceTemplate(
            uriTemplate="chatvolt://conversation/{conversationId}",
            name="Conversation Details",
            description="Get detailed information about a specific conversation",
            mimeType="application/json",
        ),
        types.ResourceTemplate(
            uriTemplate="chatvolt://contact/{contactId}",
            name="Contact Profile",
            description="Get detailed information about a specific contact",
            mimeType="application/json",
        ),
        types.ResourceTemplate(
            uriTemplate="chatvolt://dispatch/{dispatchId}",
            name="Dispatch Details",
            description="Get detailed information about a specific dispatch",
            mimeType="application/json",
        ),
        types.ResourceTemplate(
            uriTemplate="chatvolt://datastore/{datastoreId}",
            name="Datastore Configuration",
            description="Get detailed information about a specific datastore",
            mimeType="application/json",
        ),
        types.ResourceTemplate(
            uriTemplate="chatvolt://voltapi/{functionName}",
            name="VoltAPI Function Details",
            description="Get the source code and metadata of a VoltAPI sandboxed function by name",
            mimeType="application/json",
        ),
    ]


# --- Completions ---

COMPLETION_VALUES = {
    "modelName": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "claude-3-5-sonnet",
        "claude-3-5-haiku",
        "claude-3-opus",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "mistral-large",
        "llama-3-70b",
    ],
    "status": ["RESOLVED", "UNRESOLVED", "HUMAN_REQUESTED"],
    "channel": ["whatsapp", "telegram", "zapi", "instagram", "website", "twilio"],
    "type": [
        "http",
        "datastore",
        "mark_as_resolved",
        "request_human",
        "delayed_responses",
        "follow_up_messages",
    ],
    "method": ["GET", "POST", "PUT", "DELETE", "PATCH"],
    "defaultStatus": ["RESOLVED", "UNRESOLVED", "HUMAN_REQUESTED", "null"],
    "defaultPriority": ["LOW", "MEDIUM", "HIGH", "null"],
    "visibility": ["public", "private"],
    "priority": ["LOW", "MEDIUM", "HIGH", "URGENT"],
    "direction": ["inbound", "outbound"],
    "messageType": ["text", "image", "audio", "video", "document", "sticker"],
    "toolType": [
        "http",
        "datastore",
        "mark_as_resolved",
        "request_human",
        "delayed_responses",
        "follow_up_messages",
    ],
    "webhookType": ["whatsapp", "telegram", "zapi", "instagram"],
    "integrationType": [
        "http",
        "datastore",
        "mark_as_resolved",
        "request_human",
        "delayed_responses",
        "follow_up_messages",
        "form",
    ],
    "contentType": [
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data",
        "text/plain",
    ],
    "dispatchStatus": ["pending", "sending", "completed", "failed"],
    "presencePenalty": ["-2.0", "-1.5", "-1.0", "-0.5", "0.0", "0.5", "1.0", "1.5", "2.0"],
    "frequencyPenalty": ["-2.0", "-1.5", "-1.0", "-0.5", "0.0", "0.5", "1.0", "1.5", "2.0"],
    "topP": ["0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"],
    "temperature": ["0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"],
}


@app.completion()
async def handle_complete(
    ref: types.PromptReference | types.ResourceTemplateReference,
    argument: types.CompletionArgument,
    context: types.CompletionContext | None = None,
) -> types.Completion | None:
    """Provide completion suggestions for argument values."""
    arg_name = argument.name
    arg_value = argument.value

    # Suggest model names
    if arg_name == "modelName":
        values = [v for v in COMPLETION_VALUES["modelName"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values[:10], total=None, hasMore=None)

    # Suggest status values
    if arg_name in ("status", "defaultStatus"):
        values = COMPLETION_VALUES.get("status" if arg_name == "status" else "defaultStatus", [])
        values = [v for v in values if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest priority values
    if arg_name in ("defaultPriority", "priority"):
        values = [v for v in COMPLETION_VALUES["priority"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest channel values
    if arg_name == "channel":
        values = [v for v in COMPLETION_VALUES["channel"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest tool type values
    if arg_name in ("type", "toolType"):
        values = [v for v in COMPLETION_VALUES["type"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest HTTP method values
    if arg_name == "method":
        values = [v for v in COMPLETION_VALUES["method"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest visibility values
    if arg_name == "visibility":
        values = [v for v in COMPLETION_VALUES["visibility"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest direction values
    if arg_name == "direction":
        values = [v for v in COMPLETION_VALUES["direction"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest message type values
    if arg_name == "messageType":
        values = [v for v in COMPLETION_VALUES["messageType"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest webhook type values
    if arg_name == "webhookType":
        values = [v for v in COMPLETION_VALUES["webhookType"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest webhook type values (from toggle_webhook tool)
    if arg_name == "type" and "webhook" in str(arg_value):
        values = [v for v in COMPLETION_VALUES["webhookType"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest integration type values
    if arg_name == "integrationType":
        values = [v for v in COMPLETION_VALUES["integrationType"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest content type values
    if arg_name in ("contentType", "content_type"):
        values = [v for v in COMPLETION_VALUES["contentType"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest dispatch status values
    if arg_name == "status":
        values = [v for v in COMPLETION_VALUES["dispatchStatus"] if arg_value.lower() in v.lower()]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest presence penalty values
    if arg_name == "presencePenalty":
        values = [v for v in COMPLETION_VALUES["presencePenalty"] if arg_value in v]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest frequency penalty values
    if arg_name == "frequencyPenalty":
        values = [v for v in COMPLETION_VALUES["frequencyPenalty"] if arg_value in v]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest topP values
    if arg_name == "topP":
        values = [v for v in COMPLETION_VALUES["topP"] if arg_value in v]
        return types.Completion(values=values, total=None, hasMore=None)

    # Suggest temperature values
    if arg_name == "temperature":
        values = [v for v in COMPLETION_VALUES["temperature"] if arg_value in v]
        return types.Completion(values=values, total=None, hasMore=None)

    return None


# --- Tools ---


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return registry.get_tool_list()


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    return await registry.call_tool(name, arguments or {})


# --- Prompts ---


@app.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available prompts."""
    return list(PROMPTS.values())


@app.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    """Get a specific prompt."""
    return get_prompt_message(name, arguments or {})


# StreamableHTTP transport (stateless + JSON response).
# No SSE, no sessions — each HTTP request is independent.
# Clients POST JSON-RPC messages and receive JSON-RPC responses.
session_manager = StreamableHTTPSessionManager(
    app=app,
    json_response=True,
    stateless=True,
)


@contextlib.asynccontextmanager
async def lifespan(starlette_app: Starlette) -> AsyncIterator[None]:
    """Lifespan context: starts and stops the Streamable HTTP session manager."""
    async with session_manager.run():
        yield


async def mcp_asgi_handler(scope, receive, send):
    """
    ASGI handler for MCP requests.

    - Extracts and stores the Authorization header for request-scoped access.
    - Delegates to StreamableHTTPSessionManager which handles the protocol.
    - Mounted at /sse for backward compatibility (uses Streamable HTTP, not SSE).
    - Returns raw ASGI responses (the session manager already sends them).
    """
    if scope["type"] != "http":
        return

    # Extract and store auth token from request
    headers = dict(scope.get("headers", []) or [])
    auth_value = headers.get(b"authorization", b"").decode("utf-8", errors="ignore")
    if auth_value:
        if auth_value.lower().startswith("bearer "):
            token = auth_value[7:]
        else:
            token = auth_value
        set_request_auth_token(token)

    await session_manager.handle_request(scope, receive, send)


_starlette_app = Starlette(
    lifespan=lifespan,
    routes=[
        # Mount the MCP ASGI handler at /sse/ (trailing slash required by Mount).
        # Using Mount (not Route) because mcp_asgi_handler is a raw ASGI app
        # that sends its own response via the ASGI send() callable.
        Mount("/sse/", app=mcp_asgi_handler),
    ],
    middleware=[Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])],
)


class _CompatASGI:
    """
    Thin ASGI wrapper that normalizes /sse → /sse/ so both paths work.

    Starlette's Mount redirects /sse (no trailing slash) to /sse/ with a 307.
    Many MCP clients don't follow 307 redirects for POST, so we normalize
    the path at the ASGI level before Starlette sees it.
    """

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            # Normalize /sse → /sse/ so Mount matches without redirecting
            if path.rstrip("/") == "/sse":
                scope = dict(scope)
                scope["path"] = "/sse/"
        await _starlette_app(scope, receive, send)


starlette_app = _CompatASGI()
