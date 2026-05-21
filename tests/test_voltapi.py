"""Tests for VoltAPI proxy tools, resources, and prompts."""

import json

import pytest
import respx

from src.config import VOLTAPI_BASE_URL
from src.server import handle_list_resource_templates, handle_list_resources, handle_list_tools, handle_read_resource
from src.tools.loader import ToolRegistry

VOLTAPI_TOOLS = [
    "voltapi_list_functions",
    "voltapi_get_function",
    "voltapi_create_function",
    "voltapi_rename_function",
    "voltapi_toggle_function",
    "voltapi_delete_function",
    "voltapi_execute_function",
]


@pytest.fixture
def registry():
    return ToolRegistry()


def _voltapi_url(path: str) -> str:
    """Build a VoltAPI proxy URL for the given path."""
    return f"{VOLTAPI_BASE_URL}?path={path}"


# =========================================================================
# Tool Existence & Annotations
# =========================================================================


class TestVoltapiToolExistence:
    """Verify all VoltAPI tools are registered and have correct metadata."""

    @pytest.mark.asyncio
    async def test_all_voltapi_tools_exist(self):
        tools = await handle_list_tools()
        names = {t.name for t in tools}
        for name in VOLTAPI_TOOLS:
            assert name in names, f"Missing VoltAPI tool: {name}"

    @pytest.mark.asyncio
    async def test_voltapi_tools_have_voltapi_flag(self, registry):
        for name in VOLTAPI_TOOLS:
            info = registry.tools[name]
            assert info.get("voltapi") is True, f"{name} should have voltapi=True"

    @pytest.mark.asyncio
    async def test_voltapi_list_get_have_readonly_annotation(self):
        tools = await handle_list_tools()
        for tool in tools:
            if tool.name in ("voltapi_list_functions", "voltapi_get_function"):
                assert tool.annotations.readOnlyHint is True, f"{tool.name} should be readOnlyHint=True"

    @pytest.mark.asyncio
    async def test_voltapi_delete_has_destructive_annotation(self):
        tools = await handle_list_tools()
        for tool in tools:
            if tool.name == "voltapi_delete_function":
                assert tool.annotations.destructiveHint is True, f"{tool.name} should be destructiveHint=True"

    @pytest.mark.asyncio
    async def test_voltapi_create_rename_toggle_execute_not_readonly(self):
        tools = await handle_list_tools()
        for tool in tools:
            if tool.name in (
                "voltapi_create_function",
                "voltapi_rename_function",
                "voltapi_toggle_function",
                "voltapi_execute_function",
            ):
                assert tool.annotations.readOnlyHint is False, f"{tool.name} should NOT be readOnlyHint=True"


# =========================================================================
# Tool Calls — voltapi_list_functions
# =========================================================================


class TestVoltapiListFunctions:
    @pytest.mark.asyncio
    @respx.mock
    async def test_list_functions_success(self, registry):
        """List functions returns an array of function objects."""
        mock_response = [
            {"id": "f1", "name": "func-a", "is_disabled": 0},
            {"id": "f2", "name": "func-b", "is_disabled": 1},
        ]
        route = respx.post(_voltapi_url("functions")).respond(status_code=200, json=mock_response)

        result = await registry.call_tool("voltapi_list_functions", {})
        parsed = json.loads(result[0].text)
        assert parsed == mock_response
        assert route.called

        # Verify the body contains _method: GET
        body = json.loads(route.calls.last.request.content)
        assert body == {"_method": "GET"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_functions_empty(self, registry):
        """Empty list is still valid."""
        route = respx.post(_voltapi_url("functions")).respond(status_code=200, json=[])
        result = await registry.call_tool("voltapi_list_functions", {})
        parsed = json.loads(result[0].text)
        assert parsed == []
        assert route.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_functions_http_error(self, registry):
        """Server error is propagated."""
        respx.post(_voltapi_url("functions")).respond(status_code=500, text="Internal Server Error")
        result = await registry.call_tool("voltapi_list_functions", {})
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 500


# =========================================================================
# Tool Calls — voltapi_get_function
# =========================================================================


class TestVoltapiGetFunction:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_function_success(self, registry):
        """Get function by name returns the function object with code."""
        mock_response = {
            "id": "f1",
            "name": "my-func",
            "code": "async (input) => input",
            "is_disabled": 0,
        }
        route = respx.post(_voltapi_url("functions/my-func")).respond(status_code=200, json=mock_response)

        result = await registry.call_tool("voltapi_get_function", {"name": "my-func"})
        parsed = json.loads(result[0].text)
        assert parsed == mock_response
        assert route.called

        body = json.loads(route.calls.last.request.content)
        assert body == {"_method": "GET"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_function_not_found(self, registry):
        """Non-existent function returns 404."""
        respx.post(_voltapi_url("functions/nonexistent")).respond(
            status_code=404, json={"error": "Function not found"}
        )
        result = await registry.call_tool("voltapi_get_function", {"name": "nonexistent"})
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 404

    @pytest.mark.asyncio
    async def test_get_function_missing_name(self, registry):
        """Missing required name returns validation error."""
        result = await registry.call_tool("voltapi_get_function", {})
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 400


# =========================================================================
# Tool Calls — voltapi_create_function
# =========================================================================


class TestVoltapiCreateFunction:
    @pytest.mark.asyncio
    @respx.mock
    async def test_create_function_success(self, registry):
        """Create function with name and code."""
        route = respx.post(_voltapi_url("functions")).respond(
            status_code=200, json={"message": "Function created/updated successfully."}
        )

        result = await registry.call_tool(
            "voltapi_create_function",
            {"name": "my-script", "code": "async (input) => input"},
        )
        parsed = json.loads(result[0].text)
        assert parsed == {"message": "Function created/updated successfully."}
        assert route.called

        body = json.loads(route.calls.last.request.content)
        assert body["name"] == "my-script"
        assert body["code"] == "async (input) => input"
        # No _method for POST operations
        assert "_method" not in body

    @pytest.mark.asyncio
    async def test_create_function_missing_name(self, registry):
        """Missing required name returns validation error."""
        result = await registry.call_tool("voltapi_create_function", {"code": "async (i) => i"})
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 400

    @pytest.mark.asyncio
    async def test_create_function_missing_code(self, registry):
        """Missing required code returns validation error."""
        result = await registry.call_tool("voltapi_create_function", {"name": "test"})
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 400


# =========================================================================
# Tool Calls — voltapi_rename_function
# =========================================================================


class TestVoltapiRenameFunction:
    @pytest.mark.asyncio
    @respx.mock
    async def test_rename_function_success(self, registry):
        """Rename sends PUT via _method with newName."""
        route = respx.post(_voltapi_url("functions/old-name")).respond(
            status_code=200, json={"message": "Function renamed successfully."}
        )

        result = await registry.call_tool(
            "voltapi_rename_function",
            {"name": "old-name", "newName": "new-name"},
        )
        parsed = json.loads(result[0].text)
        assert parsed == {"message": "Function renamed successfully."}
        assert route.called

        body = json.loads(route.calls.last.request.content)
        assert body["_method"] == "PUT"
        assert body["newName"] == "new-name"

    @pytest.mark.asyncio
    async def test_rename_function_missing_new_name(self, registry):
        """Missing newName returns validation error."""
        result = await registry.call_tool("voltapi_rename_function", {"name": "old-name"})
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 400


# =========================================================================
# Tool Calls — voltapi_toggle_function
# =========================================================================


class TestVoltapiToggleFunction:
    @pytest.mark.asyncio
    @respx.mock
    async def test_toggle_function_disable(self, registry):
        """Disable function via PATCH with is_disabled=true."""
        route = respx.post(_voltapi_url("functions/f1")).respond(
            status_code=200, json={"message": "Function updated successfully."}
        )

        result = await registry.call_tool(
            "voltapi_toggle_function",
            {"id": "f1", "is_disabled": True},
        )
        parsed = json.loads(result[0].text)
        assert parsed == {"message": "Function updated successfully."}
        assert route.called

        body = json.loads(route.calls.last.request.content)
        assert body["_method"] == "PATCH"
        assert body["is_disabled"] is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_toggle_function_enable(self, registry):
        """Enable function via PATCH with is_disabled=false."""
        route = respx.post(_voltapi_url("functions/f1")).respond(
            status_code=200, json={"message": "Function updated successfully."}
        )

        result = await registry.call_tool(
            "voltapi_toggle_function",
            {"id": "f1", "is_disabled": False},
        )
        parsed = json.loads(result[0].text)
        assert parsed == {"message": "Function updated successfully."}
        assert route.called

        body = json.loads(route.calls.last.request.content)
        assert body["_method"] == "PATCH"
        assert body["is_disabled"] is False

    @pytest.mark.asyncio
    async def test_toggle_function_missing_id(self, registry):
        """Missing id returns validation error."""
        result = await registry.call_tool("voltapi_toggle_function", {"is_disabled": True})
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 400


# =========================================================================
# Tool Calls — voltapi_delete_function
# =========================================================================


class TestVoltapiDeleteFunction:
    @pytest.mark.asyncio
    @respx.mock
    async def test_delete_function_success(self, registry):
        """Delete sends DELETE via _method."""
        route = respx.post(_voltapi_url("functions/my-func")).respond(
            status_code=200, json={"message": "Function deleted successfully."}
        )

        result = await registry.call_tool("voltapi_delete_function", {"name": "my-func"})
        parsed = json.loads(result[0].text)
        assert parsed == {"message": "Function deleted successfully."}
        assert route.called

        body = json.loads(route.calls.last.request.content)
        assert body == {"_method": "DELETE"}

    @pytest.mark.asyncio
    async def test_delete_function_missing_name(self, registry):
        """Missing name returns validation error."""
        result = await registry.call_tool("voltapi_delete_function", {})
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 400


# =========================================================================
# Tool Calls — voltapi_execute_function
# =========================================================================


class TestVoltapiExecuteFunction:
    @pytest.mark.asyncio
    @respx.mock
    async def test_execute_function_success(self, registry):
        """Execute sends payload as the request body."""
        mock_response = {
            "result": {"pong": True, "received": {"userId": 42}},
            "logs": ["Processing input..."],
        }
        route = respx.post(_voltapi_url("functions/my-func/execute")).respond(
            status_code=200, json=mock_response
        )

        result = await registry.call_tool(
            "voltapi_execute_function",
            {"name": "my-func", "payload": {"userId": 42}},
        )
        parsed = json.loads(result[0].text)
        assert parsed == mock_response
        assert route.called

        # Payload should be the request body directly (not wrapped in a key)
        body = json.loads(route.calls.last.request.content)
        assert body == {"userId": 42}
        # No _method for POST operations
        assert "_method" not in body

    @pytest.mark.asyncio
    @respx.mock
    async def test_execute_function_no_payload(self, registry):
        """Execute with empty object when no payload is provided."""
        route = respx.post(_voltapi_url("functions/my-func/execute")).respond(
            status_code=200, json={"result": {}, "logs": []}
        )

        await registry.call_tool(
            "voltapi_execute_function",
            {"name": "my-func"},
        )
        assert route.called

        body = json.loads(route.calls.last.request.content)
        assert body == {}

    @pytest.mark.asyncio
    @respx.mock
    async def test_execute_function_disabled(self, registry):
        """Disabled function returns 400."""
        respx.post(_voltapi_url("functions/disabled-func/execute")).respond(
            status_code=400, json={"error": "Function is disabled."}
        )

        result = await registry.call_tool(
            "voltapi_execute_function",
            {"name": "disabled-func", "payload": {}},
        )
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 400

    @pytest.mark.asyncio
    @respx.mock
    async def test_execute_function_runtime_error(self, registry):
        """Runtime error in sandbox returns 500 with details."""
        respx.post(_voltapi_url("functions/broken-func/execute")).respond(
            status_code=500,
            json={"error": "Runtime error", "details": "TypeError: ...", "logs": ["Error occurred"]},
        )

        result = await registry.call_tool(
            "voltapi_execute_function",
            {"name": "broken-func", "payload": {}},
        )
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 500
        assert "details" in parsed["message"]

    @pytest.mark.asyncio
    async def test_execute_function_missing_name(self, registry):
        """Missing name returns validation error."""
        result = await registry.call_tool("voltapi_execute_function", {"payload": {}})
        parsed = json.loads(result[0].text)
        assert parsed["error"] is True
        assert parsed["status"] == 400


# =========================================================================
# URL Construction
# =========================================================================


class TestVoltapiUrlConstruction:
    """Verify the correct VoltAPI proxy URL is used for each tool."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_functions_url(self, registry):
        route = respx.post(f"{VOLTAPI_BASE_URL}?path=functions").respond(status_code=200, json=[])
        await registry.call_tool("voltapi_list_functions", {})
        assert route.called
        assert str(route.calls.last.request.url).startswith(f"{VOLTAPI_BASE_URL}?path=functions")

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_function_url(self, registry):
        route = respx.post(f"{VOLTAPI_BASE_URL}?path=functions/myfunc").respond(status_code=200, json={})
        await registry.call_tool("voltapi_get_function", {"name": "myfunc"})
        assert route.called
        assert "?path=functions/myfunc" in str(route.calls.last.request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_create_function_url(self, registry):
        route = respx.post(f"{VOLTAPI_BASE_URL}?path=functions").respond(status_code=200, json={})
        await registry.call_tool("voltapi_create_function", {"name": "f", "code": "async (i) => i"})
        assert route.called
        assert "?path=functions" in str(route.calls.last.request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_execute_function_url(self, registry):
        route = respx.post(f"{VOLTAPI_BASE_URL}?path=functions/myfunc/execute").respond(status_code=200, json={})
        await registry.call_tool("voltapi_execute_function", {"name": "myfunc", "payload": {}})
        assert route.called
        assert "?path=functions/myfunc/execute" in str(route.calls.last.request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_all_voltapi_use_post(self, registry):
        """All voltapi tools should use POST as the HTTP method."""
        args_by_tool = {
            "voltapi_list_functions": {},
            "voltapi_get_function": {"name": "dummy"},
            "voltapi_create_function": {"name": "dummy", "code": "async (i) => i"},
            "voltapi_rename_function": {"name": "dummy", "newName": "new-dummy"},
            "voltapi_toggle_function": {"id": "dummy-id", "is_disabled": False},
            "voltapi_delete_function": {"name": "dummy"},
            "voltapi_execute_function": {"name": "dummy", "payload": {}},
        }
        url_by_tool = {
            "voltapi_list_functions": _voltapi_url("functions"),
            "voltapi_get_function": _voltapi_url("functions/dummy"),
            "voltapi_create_function": _voltapi_url("functions"),
            "voltapi_rename_function": _voltapi_url("functions/dummy"),
            "voltapi_toggle_function": _voltapi_url("functions/dummy-id"),
            "voltapi_delete_function": _voltapi_url("functions/dummy"),
            "voltapi_execute_function": _voltapi_url("functions/dummy/execute"),
        }
        for name in VOLTAPI_TOOLS:
            route = respx.post(url_by_tool[name]).respond(status_code=200, json={})
            await registry.call_tool(name, args_by_tool[name])
            assert route.called, f"{name} should use POST"
            assert route.calls.last.request.method == "POST", f"{name} method should be POST"
            route.reset()


# =========================================================================
# Resources
# =========================================================================


class TestVoltapiResources:
    @pytest.mark.asyncio
    async def test_voltapi_guide_resource_exists(self):
        resources = await handle_list_resources()
        uris = {str(r.uri) for r in resources}
        assert "chatvolt://voltapi-guide" in uris

    @pytest.mark.asyncio
    async def test_voltapi_guide_resource_content(self):
        result = await handle_read_resource("chatvolt://voltapi-guide")
        assert isinstance(result, str)
        assert "VoltAPI" in result
        assert "async (input)" in result
        assert "fetch" in result
        assert "console.log" in result
        assert "voltApi.get" in result
        assert "10s" in result
        assert "128MB" in result

    @pytest.mark.asyncio
    async def test_voltapi_function_resource_template(self):
        """chatvolt://voltapi/{functionName} should be a registered template."""
        resources = await handle_list_resource_templates()
        uris = [str(r.uriTemplate) for r in resources]
        assert "chatvolt://voltapi/{functionName}" in uris


# =========================================================================
# Prompt
# =========================================================================


class TestVoltapiPrompt:
    @pytest.mark.asyncio
    async def test_create_voltapi_function_prompt_exists(self):
        from src.prompts.workflows import PROMPTS

        assert "create_voltapi_function" in PROMPTS
        prompt = PROMPTS["create_voltapi_function"]
        assert "voltapi" in prompt.description.lower() or "VoltAPI" in prompt.description


# =========================================================================
# Edge Cases
# =========================================================================


class TestVoltapiEdgeCases:
    @pytest.mark.asyncio
    @respx.mock
    async def test_execute_payload_is_object(self, registry):
        """Payload that is not a dict gets wrapped."""
        route = respx.post(_voltapi_url("functions/f/execute")).respond(status_code=200, json={"result": {}})
        await registry.call_tool(
            "voltapi_execute_function",
            {"name": "f", "payload": "raw_string"},
        )
        body = json.loads(route.calls.last.request.content)
        assert body == {"value": "raw_string"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_execute_payload_number(self, registry):
        """Number payload gets wrapped in dict."""
        route = respx.post(_voltapi_url("functions/f/execute")).respond(status_code=200, json={"result": {}})
        await registry.call_tool(
            "voltapi_execute_function",
            {"name": "f", "payload": 42},
        )
        body = json.loads(route.calls.last.request.content)
        assert body == {"value": 42}

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_function_name_rejected(self, registry):
        """Empty name should still be handled by the API."""
        route = respx.post(_voltapi_url("functions/")).respond(status_code=404, json={"error": "Not found"})
        await registry.call_tool("voltapi_get_function", {"name": ""})
        assert route.called
