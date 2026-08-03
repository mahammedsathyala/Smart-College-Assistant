"""Smart College Assistant — Policy Agent"""
from agents.base_agent import BaseAgent
from prompts.system_prompts import POLICY_SYSTEM_PROMPT


class PolicyAgent(BaseAgent):
    """Handles college policies, rules, and regulations."""
    name = "policy_agent"
    system_prompt = POLICY_SYSTEM_PROMPT
