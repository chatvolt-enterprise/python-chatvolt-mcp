import pytest

from src.prompts.workflows import PROMPTS, get_prompt_message


@pytest.mark.asyncio
async def test_onboard_new_user_prompt():
    """Test onboard_new_user prompt with required arguments."""
    result = get_prompt_message("onboard_new_user", {"first_name": "John", "phone_number": "+5511988887777"})
    assert result.description == "Onboarding Workflow"
    assert len(result.messages) == 1
    assert result.messages[0].role == "user"
    assert "John" in result.messages[0].content.text
    assert "+5511988887777" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_broadcast_campaign_prompt():
    """Test broadcast_campaign prompt."""
    result = get_prompt_message("broadcast_campaign", {"campaign_name": "Summer Sale"})
    assert result.description == "Broadcast Campaign Workflow"
    assert "Summer Sale" in result.messages[0].content.text
    assert "list_contacts" in result.messages[0].content.text
    assert "create_dispatch" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_create_new_agent_prompt():
    """Test create_new_agent prompt."""
    result = get_prompt_message("create_new_agent", {"agent_name": "Sales Bot"})
    assert result.description == "Agent Creation Workflow"
    assert "Sales Bot" in result.messages[0].content.text
    assert "create_agent" in result.messages[0].content.text
    assert "get_models" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_create_new_agent_default_name():
    """Test create_new_agent prompt with no name."""
    result = get_prompt_message("create_new_agent", {})
    assert "a new agent" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_setup_datastore_prompt():
    """Test setup_datastore prompt."""
    result = get_prompt_message("setup_datastore", {"datastore_name": "Knowledge Base"})
    assert result.description == "Datastore Setup Workflow"
    assert "Knowledge Base" in result.messages[0].content.text
    assert "create_datastore" in result.messages[0].content.text
    assert "create_datasource" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_create_crm_workflow_prompt():
    """Test create_crm_workflow prompt."""
    result = get_prompt_message("create_crm_workflow", {"scenario_name": "Sales Pipeline"})
    assert result.description == "CRM Workflow Creation"
    assert "Sales Pipeline" in result.messages[0].content.text
    assert "create_crm_scenario" in result.messages[0].content.text
    assert "create_crm_step" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_whatsapp_outreach_prompt():
    """Test whatsapp_outreach prompt."""
    result = get_prompt_message("whatsapp_outreach", {"phone": "+5511988887777", "instance_id": "abc123"})
    assert result.description == "WhatsApp Outreach"
    assert "+5511988887777" in result.messages[0].content.text
    assert "abc123" in result.messages[0].content.text
    assert "zapi_send_text" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_contact_enrichment_with_id():
    """Test contact_enrichment prompt with contact ID."""
    result = get_prompt_message("contact_enrichment", {"contact_id": "contact_123"})
    assert result.description == "Contact Enrichment"
    assert "contact_123" in result.messages[0].content.text
    assert "get_contact" in result.messages[0].content.text
    assert "list_contacts" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_contact_enrichment_without_id():
    """Test contact_enrichment prompt without contact ID."""
    result = get_prompt_message("contact_enrichment", {})
    assert result.description == "Contact Enrichment"
    assert "No specific contact ID" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_agent_health_check_prompt():
    """Test agent_health_check prompt."""
    result = get_prompt_message("agent_health_check", {"agent_id": "agent_abc"})
    assert result.description == "Agent Health Check"
    assert "agent_abc" in result.messages[0].content.text
    assert "get_agent" in result.messages[0].content.text
    assert "list_conversations" in result.messages[0].content.text
    assert "get_agent_tools" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_invalid_prompt():
    """Test that invalid prompt raises ValueError."""
    with pytest.raises(ValueError, match="Unknown prompt"):
        get_prompt_message("nonexistent_prompt", {})


def test_prompts_dict_contains_all():
    """Test that PROMPTS dict contains all expected prompts."""
    expected = [
        "onboard_new_user",
        "broadcast_campaign",
        "create_new_agent",
        "setup_datastore",
        "create_crm_workflow",
        "whatsapp_outreach",
        "contact_enrichment",
        "agent_health_check",
        "create_voltapi_function",
    ]
    assert set(expected) == set(PROMPTS.keys())


def test_prompts_have_descriptions():
    """Test that all prompts have descriptions."""
    for name, prompt in PROMPTS.items():
        assert prompt.name == name
        assert prompt.description
        assert prompt.description != ""
