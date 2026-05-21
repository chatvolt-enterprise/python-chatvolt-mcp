import pytest

from src.server import (
    COMPLETION_VALUES,
    LOG_LEVELS,
    app,
    handle_complete,
    handle_get_prompt,
    handle_list_prompts,
    handle_list_resource_templates,
    handle_list_resources,
    handle_list_tools,
    handle_read_resource,
    handle_set_logging_level,
)


@pytest.mark.asyncio
async def test_server_tools_list():
    tools = await handle_list_tools()
    # The tools list should contain tools from our registry
    assert len(tools) > 0
    names = [t.name for t in tools]
    assert "query_agent" in names


@pytest.mark.asyncio
async def test_server_prompts_list():
    prompts = await handle_list_prompts()
    # We should have prompts available
    assert len(prompts) > 0
    names = [p.name for p in prompts]
    assert "create_new_agent" in names


@pytest.mark.asyncio
async def test_set_logging_level_valid():
    """Test setting valid log levels."""
    for level in LOG_LEVELS:
        result = await handle_set_logging_level(level)
        assert result is not None


@pytest.mark.asyncio
async def test_set_logging_level_invalid():
    """Test that invalid log levels raise ValueError."""
    with pytest.raises(ValueError):
        await handle_set_logging_level("invalid_level")

    with pytest.raises(ValueError):
        await handle_set_logging_level("")

    with pytest.raises(ValueError):
        await handle_set_logging_level("DEBUG")


def test_server_initialization():
    """Test that server has proper metadata and capabilities."""
    init_opts = app.create_initialization_options()
    assert init_opts.server_name == "chatvolt-mcp"
    assert init_opts.server_version == "1.0.0"
    assert init_opts.instructions is not None
    assert "Chatvolt" in init_opts.instructions
    assert init_opts.capabilities.tools is not None


def test_server_capabilities_basic():
    """Test that server declares basic tool capabilities."""
    init_opts = app.create_initialization_options()
    caps = init_opts.capabilities
    assert caps.tools is not None
    assert caps.resources is not None
    assert caps.prompts is not None
    assert caps.completions is not None
    assert caps.logging is not None


@pytest.mark.asyncio
async def test_list_resources():
    """Test listing resources."""
    resources = await handle_list_resources()
    assert len(resources) == 4
    names = [r.name for r in resources]
    assert "Available LLM Models" in names
    assert "All MCP Tools" in names
    assert "All Workflow Prompts" in names
    assert "VoltAPI Script Writing Guide" in names


@pytest.mark.asyncio
async def test_read_resource_models():
    """Test reading the models resource."""
    result = await handle_read_resource("chatvolt://models")
    assert "get_models" in result


@pytest.mark.asyncio
async def test_read_resource_tools():
    """Test reading the tools resource."""
    result = await handle_read_resource("chatvolt://tools")
    assert "query_agent" in result


@pytest.mark.asyncio
async def test_read_resource_prompts():
    """Test reading the prompts resource."""
    result = await handle_read_resource("chatvolt://prompts")
    assert "onboard_new_user" in result


@pytest.mark.asyncio
async def test_read_resource_unknown():
    """Test reading unknown resource raises ValueError."""
    with pytest.raises(ValueError, match="Unknown resource"):
        await handle_read_resource("chatvolt://unknown")


@pytest.mark.asyncio
async def test_list_resource_templates():
    """Test listing resource templates."""
    templates = await handle_list_resource_templates()
    assert len(templates) == 6
    template_names = [t.name for t in templates]
    assert "Agent Configuration" in template_names
    assert "Conversation Details" in template_names
    assert "Contact Profile" in template_names
    assert "Dispatch Details" in template_names
    assert "Datastore Configuration" in template_names
    assert "VoltAPI Function Details" in template_names


@pytest.mark.asyncio
async def test_completion_model_name():
    """Test completion for modelName."""
    result = await handle_complete(
        ref=type("PromptReference", (), {"type": "prompt", "name": "test"})(),
        argument=type("CompletionArgument", (), {"name": "modelName", "value": "gpt"})(),
        context=None,
    )
    assert result is not None
    assert len(result.values) > 0
    assert any("gpt" in v.lower() for v in result.values)


@pytest.mark.asyncio
async def test_completion_status():
    """Test completion for status."""
    result = await handle_complete(
        ref=type("PromptReference", (), {"type": "prompt", "name": "test"})(),
        argument=type("CompletionArgument", (), {"name": "status", "value": "RES"})(),
        context=None,
    )
    assert result is not None
    assert "RESOLVED" in result.values


@pytest.mark.asyncio
async def test_completion_channel():
    """Test completion for channel."""
    result = await handle_complete(
        ref=type("PromptReference", (), {"type": "prompt", "name": "test"})(),
        argument=type("CompletionArgument", (), {"name": "channel", "value": "what"})(),
        context=None,
    )
    assert result is not None
    assert "whatsapp" in result.values


@pytest.mark.asyncio
async def test_completion_type():
    """Test completion for type."""
    result = await handle_complete(
        ref=type("PromptReference", (), {"type": "prompt", "name": "test"})(),
        argument=type("CompletionArgument", (), {"name": "type", "value": "http"})(),
        context=None,
    )
    assert result is not None
    assert "http" in result.values


@pytest.mark.asyncio
async def test_completion_method():
    """Test completion for method."""
    result = await handle_complete(
        ref=type("PromptReference", (), {"type": "prompt", "name": "test"})(),
        argument=type("CompletionArgument", (), {"name": "method", "value": "GET"})(),
        context=None,
    )
    assert result is not None
    assert "GET" in result.values


@pytest.mark.asyncio
async def test_completion_default_priority():
    """Test completion for defaultPriority."""
    result = await handle_complete(
        ref=type("PromptReference", (), {"type": "prompt", "name": "test"})(),
        argument=type("CompletionArgument", (), {"name": "defaultPriority", "value": "HIGH"})(),
        context=None,
    )
    assert result is not None
    assert "HIGH" in result.values


@pytest.mark.asyncio
async def test_completion_no_match():
    """Test completion returns None for unknown arguments."""
    result = await handle_complete(
        ref=type("PromptReference", (), {"type": "prompt", "name": "test"})(),
        argument=type("CompletionArgument", (), {"name": "unknown_arg", "value": "test"})(),
        context=None,
    )
    assert result is None


@pytest.mark.asyncio
async def test_get_prompt():
    """Test getting a specific prompt."""
    result = await handle_get_prompt("create_new_agent", {"agent_name": "Test Bot"})
    assert result is not None
    assert "Test Bot" in result.messages[0].content.text


def test_completion_values_defined():
    """Test that COMPLETION_VALUES has expected keys."""
    assert "modelName" in COMPLETION_VALUES
    assert "status" in COMPLETION_VALUES
    assert "channel" in COMPLETION_VALUES
    assert "type" in COMPLETION_VALUES
    assert "method" in COMPLETION_VALUES
