"""Smart College Assistant — Placement Agent"""
from agents.base_agent import BaseAgent
from prompts.system_prompts import PLACEMENT_SYSTEM_PROMPT
from prompts.few_shot_prompts import PLACEMENT_FEW_SHOTS


class PlacementAgent(BaseAgent):
    """Handles placement drives, companies, and career guidance."""
    name = "placement_agent"
    system_prompt = PLACEMENT_SYSTEM_PROMPT

    def _build_prompt(self, query: str, history=None) -> str:
        examples = "\n\n".join(
            f"Student: {ex['question']}\nAssistant: {ex['answer']}"
            for ex in PLACEMENT_FEW_SHOTS
        )
        base = super()._build_prompt(query, history)
        return f"{self.system_prompt}\n\nExamples:\n{examples}\n\n{base.split('System:')[1]}"
