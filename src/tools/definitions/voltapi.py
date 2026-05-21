from typing import Any

TOOLS: dict[str, dict[str, Any]] = {
    "voltapi_create_function": {
        "method": "POST",
        "path": "functions",
        "voltapi": True,
        "description": "Create a new ChatVolt sandboxed JavaScript function via the VoltAPI proxy. "
        "The code must be an async arrow function: 'async (input) => { ... }'. "
        "The function runs in an isolated V8 isolate (isolated-vm) with 128MB memory and 10s timeout. "
        "Available inside the sandbox: console.log/.error/.warn/.info (captured as logs), "
        "fetch() with SSRF protection (blocks private IPs), "
        "voltApi.get(url) and voltApi.post(url, body) for authenticated calls back to Chatvolt APIs. "
        "NOT available: require(), import/export, fs, path, process, setTimeout, setInterval. "
        "Response: the created function object with id, name, code, is_disabled fields.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Unique identifier for the function (e.g., 'data-enricher', 'webhook-validator'). "
                    "Use kebab-case or snake_case. This name is used as the reference in execute/delete/get calls.",
                },
                "code": {
                    "type": "string",
                    "description": "JavaScript code as an async arrow function. Must start with 'async (input) => {' "
                    "and return a value. Example:\n\n"
                    'async (input) => {\n'
                    '  console.log("Processing:", input);\n'
                    '  const res = await fetch("https://api.example.com", {\n'
                    '    headers: { Authorization: "Bearer token" }\n'
                    '  });\n'
                    '  const data = await res.json();\n'
                    '  return { success: true, data };\n'
                    '}',
                },
            },
            "required": ["name", "code"],
        },
    },
    "voltapi_list_functions": {
        "method": "GET",
        "path": "functions",
        "voltapi": True,
        "description": "List all ChatVolt sandboxed functions registered in the organization "
        "via the VoltAPI proxy. Returns an array of function objects. Each object includes: "
        "id (UUID), name, is_disabled (boolean), createdAt, updatedAt. "
        "Note: the response does NOT include the function code — use voltapi_get_function for that. "
        "Use this tool to discover available functions before executing or managing them.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    "voltapi_get_function": {
        "method": "GET",
        "path": "functions/{name}",
        "voltapi": True,
        "description": "Retrieve a specific ChatVolt sandboxed function by name via the VoltAPI proxy. "
        "Returns the full function object including its 'code' (the JavaScript source), "
        "plus id (UUID), name, is_disabled, createdAt, updatedAt. "
        "Use this when you need to inspect, review, or modify an existing function's code. "
        "Use voltapi_list_functions first to discover available function names.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the function to retrieve (e.g., 'data-enricher'). "
                    "Use voltapi_list_functions to discover available names.",
                },
            },
            "required": ["name"],
        },
    },
    "voltapi_rename_function": {
        "method": "PUT",
        "path": "functions/{name}",
        "voltapi": True,
        "description": "Rename an existing ChatVolt sandboxed function via the VoltAPI proxy. "
        "Provide the current name and the desired new name. "
        "After renaming, references to the old name (voltapi_execute_function, voltapi_get_function, "
        "voltapi_delete_function) will need to use the new name. "
        "Returns the updated function object with the new name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Current name of the function to rename.",
                },
                "newName": {
                    "type": "string",
                    "description": "New name for the function. Must be unique within the organization.",
                },
            },
            "required": ["name", "newName"],
        },
    },
    "voltapi_toggle_function": {
        "method": "PATCH",
        "path": "functions/{id}",
        "voltapi": True,
        "description": "Enable or disable a ChatVolt sandboxed function via the VoltAPI proxy. "
        "IMPORTANT: This uses the function's UUID (id), NOT its name. "
        "Use voltapi_list_functions to find the id for a given function name. "
        "When a function is disabled (is_disabled: true), executing it returns a 400 error "
        "with message 'isDisabled'. Use this for temporarily taking functions offline "
        "without deleting them.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "UUID of the function to toggle. NOT the name. "
                    "Use voltapi_list_functions to get the id from the function name.",
                },
                "is_disabled": {
                    "type": "boolean",
                    "description": "true = disable the function (execution will be blocked with 400). "
                    "false = enable the function (execution resumes normally).",
                },
            },
            "required": ["id", "is_disabled"],
        },
    },
    "voltapi_delete_function": {
        "method": "DELETE",
        "path": "functions/{name}",
        "voltapi": True,
        "description": "Permanently delete a ChatVolt sandboxed function by name via the VoltAPI proxy. "
        "This action is irreversible. Use voltapi_toggle_function to temporarily disable instead. "
        "Returns a success confirmation. After deletion, any references to this function name "
        "in voltapi_execute_function will return a 404 error.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the function to delete. "
                    "Use voltapi_list_functions to discover available functions.",
                },
            },
            "required": ["name"],
        },
    },
    "voltapi_execute_function": {
        "method": "POST",
        "path": "functions/{name}/execute",
        "voltapi": True,
        "description": "Execute a ChatVolt sandboxed JavaScript function by name with an arbitrary JSON payload. "
        "The function receives the payload as its 'input' parameter. "
        "\n\n"
        "RESPONSE FORMAT:\n"
        '{\n'
        '  "result": <whatever the function returned>,\n'
        '  "logs": ["console.log output lines..."]\n'
        '}\n'
        "\n"
        "SANDBOX ENVIRONMENT:\n"
        "- Code is an async (input) => { ... } function\n"
        "- console.log/error/warn/info output is captured in 'logs' array\n"
        "- fetch(url, options) available with SSRF protection (blocks private/internal IPs)\n"
        "- voltApi.get(url) and voltApi.post(url, body) for authenticated Chatvolt API calls\n"
        "- Timeout: 10s in the VM (60s polling)\n"
        "- Memory: 128MB per execution\n"
        "- No require(), import, fs, path, process, setTimeout/setInterval\n"
        "\n"
        "ERROR RESPONSES:\n"
        "- 400: function is disabled\n"
        "- 404: function not found\n"
        '- 500: runtime error inside sandbox (details and logs in response)\n'
        "\n"
        "Use this for dynamic data transformation, API orchestration, webhook processing, "
        "and custom business logic that runs on-demand.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the function to execute (e.g., 'data-enricher'). "
                    "Use voltapi_list_functions to discover available functions.",
                },
                "payload": {
                    "type": "object",
                    "description": "Any JSON-serialisable payload to pass as 'input' to the function. "
                    "The function accesses this directly (e.g., input.userId, input.email). "
                    "Can be an empty object {} if no input is needed.",
                    "additionalProperties": True,
                },
            },
            "required": ["name"],
        },
    },
}
