from typing import Any

from .definitions.agents import TOOLS as AGENTS_TOOLS
from .definitions.artifacts import TOOLS as ARTIFACTS_TOOLS
from .definitions.blacklist import TOOLS as BLACKLIST_TOOLS
from .definitions.contacts import TOOLS as CONTACTS_TOOLS
from .definitions.conversation_mgmt import TOOLS as CONVERSATION_MGMT_TOOLS
from .definitions.conversations import TOOLS as CONVERSATIONS_TOOLS
from .definitions.crm import TOOLS as CRM_TOOLS
from .definitions.crm_logs import TOOLS as CRM_LOGS_TOOLS
from .definitions.crm_scenarios import TOOLS as CRM_SCENARIOS_TOOLS
from .definitions.datasources import TOOLS as DATASOURCES_TOOLS
from .definitions.datastores import TOOLS as DATASTORES_TOOLS
from .definitions.dispatches import TOOLS as DISPATCHES_TOOLS
from .definitions.instagram import TOOLS as INSTAGRAM_TOOLS
from .definitions.interactive import TOOLS as INTERACTIVE_TOOLS
from .definitions.mercadolivre import TOOLS as MERCADOLIVRE_TOOLS
from .definitions.telegram import TOOLS as TELEGRAM_TOOLS
from .definitions.twilio import TOOLS as TWILIO_TOOLS
from .definitions.voltapi import TOOLS as VOLTAPI_TOOLS
from .definitions.whatsapp_official import TOOLS as WHATSAPP_OFFICIAL_TOOLS
from .definitions.whitelist import TOOLS as WHITELIST_TOOLS
from .definitions.zapi import TOOLS as ZAPI_TOOLS
from .definitions.zapper import TOOLS as ZAPPER_TOOLS

TOOLS_DEFINITION: dict[str, dict[str, Any]] = {
    **AGENTS_TOOLS,
    **CONVERSATIONS_TOOLS,
    **ARTIFACTS_TOOLS,
    **DATASTORES_TOOLS,
    **CRM_TOOLS,
    **CONTACTS_TOOLS,
    **DISPATCHES_TOOLS,
    **BLACKLIST_TOOLS,
    **WHITELIST_TOOLS,
    **CONVERSATION_MGMT_TOOLS,
    **CRM_SCENARIOS_TOOLS,
    **CRM_LOGS_TOOLS,
    **DATASOURCES_TOOLS,
    **ZAPI_TOOLS,
    **WHATSAPP_OFFICIAL_TOOLS,
    **INTERACTIVE_TOOLS,
    **TWILIO_TOOLS,
    **VOLTAPI_TOOLS,
    **MERCADOLIVRE_TOOLS,
    **ZAPPER_TOOLS,
    **TELEGRAM_TOOLS,
    **INSTAGRAM_TOOLS,
}
