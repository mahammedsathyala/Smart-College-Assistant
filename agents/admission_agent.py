"""Smart College Assistant — Admission Agent"""
from agents.base_agent import BaseAgent
from prompts.system_prompts import ADMISSION_SYSTEM_PROMPT
from prompts.few_shot_prompts import ADMISSION_FEW_SHOTS


class AdmissionAgent(BaseAgent):
    """Handles all admission-related queries."""
    name = "admission_agent"
    system_prompt = ADMISSION_SYSTEM_PROMPT

    def _build_prompt(self, query: str, history=None) -> str:
        # Inject few-shot examples
        examples = "\n\n".join(
            f"Student: {ex['question']}\nAssistant: {ex['answer']}"
            for ex in ADMISSION_FEW_SHOTS
        )
        base = super()._build_prompt(query, history)
        return f"{self.system_prompt}\n\nExamples:\n{examples}\n\n{base.split('System:')[1]}"
