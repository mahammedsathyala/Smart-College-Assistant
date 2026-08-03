"""Smart College Assistant — FAQ Agent"""
from agents.base_agent import BaseAgent
from prompts.system_prompts import FAQ_SYSTEM_PROMPT


class FAQAgent(BaseAgent):
    """Handles general FAQ and helpdesk queries."""
    name = "faq_agent"
    system_prompt = FAQ_SYSTEM_PROMPT
