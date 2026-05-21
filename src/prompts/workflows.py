from mcp import types

PROMPTS = {

    "onboard_new_user": types.Prompt(
        name="onboard_new_user",
        description="A guide to creating a contact and sending a welcome message.",
        arguments=[
            types.PromptArgument(name="first_name", description="Contact's first name", required=True),
            types.PromptArgument(name="phone_number", description="Contact's phone number", required=True),
        ],
    ),
    "broadcast_campaign": types.Prompt(
        name="broadcast_campaign",
        description="Setup a dispatch for a list of contacts.",
        arguments=[types.PromptArgument(name="campaign_name", description="Name of the campaign", required=True)],
    ),
    "create_new_agent": types.Prompt(
        name="create_new_agent",
        description="Interactive workflow to design, configure, and deploy a new AI agent.",
        arguments=[types.PromptArgument(name="agent_name", description="Desired name for the agent", required=False)],
    ),
    "setup_datastore": types.Prompt(
        name="setup_datastore",
        description="Interactive workflow to create a datastore and ingest data sources.",
        arguments=[
            types.PromptArgument(name="datastore_name", description="Name for the datastore", required=True),
        ],
    ),
    "create_crm_workflow": types.Prompt(
        name="create_crm_workflow",
        description="Build a CRM workflow with scenarios and steps for customer journey management.",
        arguments=[
            types.PromptArgument(name="scenario_name", description="Name for the CRM scenario", required=True),
        ],
    ),
    "whatsapp_outreach": types.Prompt(
        name="whatsapp_outreach",
        description="Send a WhatsApp message or template to a contact via Z-API.",
        arguments=[
            types.PromptArgument(name="phone", description="Recipient phone number with country code", required=True),
            types.PromptArgument(name="instance_id", description="Z-API instance ID", required=True),
        ],
    ),
    "contact_enrichment": types.Prompt(
        name="contact_enrichment",
        description="Look up, update, or manage contact information.",
        arguments=[
            types.PromptArgument(name="contact_id", description="Contact ID to manage", required=False),
        ],
    ),
    "agent_health_check": types.Prompt(
        name="agent_health_check",
        description="Check agent status, view recent conversations, and identify issues.",
        arguments=[
            types.PromptArgument(name="agent_id", description="Agent ID to check", required=True),
        ],
    ),
    "create_voltapi_function": types.Prompt(
        name="create_voltapi_function",
        description="Guided workflow to write, test, and deploy a VoltAPI sandboxed JavaScript function.",
        arguments=[
            types.PromptArgument(name="function_name", description="Desired function name", required=False),
        ],
    ),
}


def get_prompt_message(name: str, arguments: dict) -> types.GetPromptResult:
    if name == "onboard_new_user":
        first_name = arguments.get("first_name")
        phone = arguments.get("phone_number")
        return types.GetPromptResult(
            description="Onboarding Workflow",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"I want to onboard a new user named {first_name} with phone {phone}. "
                        f"Please first use the 'create_contact' tool to create the contact, "
                        f"then ask me for a message template to send via 'zapi_send_text'.",
                    ),
                )
            ],
        )
    elif name == "broadcast_campaign":
        campaign_name = arguments.get("campaign_name")
        return types.GetPromptResult(
            description="Broadcast Campaign Workflow",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Let's set up the broadcast campaign '{campaign_name}'. "
                        f"I'll need to filter contacts first using 'list_contacts'. "
                        f"After I confirm the list, we will create a dispatch using 'create_dispatch'.",
                    ),
                )
            ],
        )
    elif name == "create_new_agent":
        agent_name = arguments.get("agent_name", "a new agent")
        return types.GetPromptResult(
            description="Agent Creation Workflow",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"I want to create {agent_name}. Let's go through the steps:\n"
                        f"1. Help me define its role and goal (description).\n"
                        f"2. Help me draft a comprehensive system prompt.\n"
                        f"3. Ask me which LLM model to use (e.g., gpt-4o, claude-3-5-sonnet). "
                        f"Use 'get_models' to see available options.\n"
                        f"4. Once we have the config, use 'create_agent' to create it.",
                    ),
                )
            ],
        )
    elif name == "setup_datastore":
        name_val = arguments.get("datastore_name")
        return types.GetPromptResult(
            description="Datastore Setup Workflow",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Let's set up a datastore called '{name_val}'.\n"
                        f"1. First, use 'create_datastore' to create the container.\n"
                        f"2. Ask me what data source type I want to add (file, URL, website, etc.).\n"
                        f"3. Based on my choice, use the appropriate tool: 'create_datasource'.\n"
                        f"4. Ask me if I want to sync the datasource immediately with 'sync_datasource'.",
                    ),
                )
            ],
        )
    elif name == "create_crm_workflow":
        scenario_name = arguments.get("scenario_name")
        return types.GetPromptResult(
            description="CRM Workflow Creation",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Let's build a CRM workflow called '{scenario_name}'.\n"
                        f"1. First use 'create_crm_scenario' to create the scenario.\n"
                        f"2. Ask me to define the steps (e.g., 'New Lead', 'Qualified', 'Contacted', 'Won/Lost').\n"
                        f"3. For each step, use 'create_crm_step' with appropriate triggers and prompts.\n"
                        f"4. Ask me about any automation (webhooks, AI prompts, human handoff).",
                    ),
                )
            ],
        )
    elif name == "whatsapp_outreach":
        phone = arguments.get("phone")
        instance_id = arguments.get("instance_id")
        return types.GetPromptResult(
            description="WhatsApp Outreach",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Send a WhatsApp message to {phone} using Z-API instance '{instance_id}'.\n"
                        f"Ask me if I want to send:\n"
                        f"- A simple text message (use 'zapi_send_text')\n"
                        f"- A media message (use 'zapi_send_media')\n"
                        f"- A template message (use 'zapi_send_template')\n"
                        f"- An interactive list (use 'zapi_send_list')\n"
                        f"- Buttons (use 'zapi_send_buttons')",
                    ),
                )
            ],
        )
    elif name == "contact_enrichment":
        contact_id = arguments.get("contact_id")
        return types.GetPromptResult(
            description="Contact Enrichment",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="Manage contact information."
                        + (
                            f" Contact ID: {contact_id}"
                            if contact_id
                            else " No specific contact ID provided - ask me for details."
                        )
                        + "\nI can help you:\n"
                        "- Look up a contact with 'get_contact' or 'list_contacts'\n"
                        "- Update contact info with 'update_contact'\n"
                        "- Add/remove tags with 'update_contact'\n"
                        "- View contact's conversation history with 'get_contact_conversations'",
                    ),
                )
            ],
        )
    elif name == "agent_health_check":
        agent_id = arguments.get("agent_id")
        return types.GetPromptResult(
            description="Agent Health Check",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Perform a health check on agent '{agent_id}'.\n"
                        f"1. Use 'get_agent' to view agent configuration.\n"
                        f"2. Use 'list_conversations' with agentId filter to see recent conversations.\n"
                        f"3. Check for unresolved conversations that may need attention.\n"
                        f"4. Review agent tools with 'get_agent_tools'.\n"
                        f"5. Report findings and suggest improvements.",
                    ),
                )
            ],
        )
    elif name == "create_voltapi_function":
        function_name = arguments.get("function_name", "my-function")
        return types.GetPromptResult(
            description="VoltAPI Function Creation Workflow",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Let's create a VoltAPI sandboxed function called '{function_name}'.\n\n"
                        "Available globals in the sandbox:\n"
                        "- input: the payload you send on execution\n"
                        "- console.log/error/warn/info: captured and returned in logs[]\n"
                        "- fetch(url, options): HTTP client with SSRF protection\n"
                        "- voltApi.get(url): GET autenticado para APIs internas do Chatvolt\n"
                        "- voltApi.post(url, body): POST autenticado para APIs internas\n\n"
                        "Limitations: no require(), fs, path, process, setTimeout/setInterval.\n"
                        "Max 10s execution, 128MB memory.\n\n"
                        "Please tell me what this function should do, and I'll help you:\n"
                        "1. Design the JavaScript code\n"
                        "2. Create the function with voltapi_create_function\n"
                        "3. Test it with voltapi_execute_function",
                    ),
                )
            ],
        )
    else:
        raise ValueError(f"Unknown prompt: {name}")
