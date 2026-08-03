"""Smart College Assistant — Exam Agent"""
from agents.base_agent import BaseAgent
from prompts.system_prompts import EXAM_SYSTEM_PROMPT
from prompts.few_shot_prompts import EXAM_FEW_SHOTS


class ExamAgent(BaseAgent):
    """Handles examination, marks, CGPA, and results queries."""
    name = "exam_agent"
    system_prompt = EXAM_SYSTEM_PROMPT

    def _build_prompt(self, query: str, history=None) -> str:
        examples = "\n\n".join(
            f"Student: {ex['question']}\nAssistant: {ex['answer']}"
            for ex in EXAM_FEW_SHOTS
        )
        base = super()._build_prompt(query, history)
        return f"{self.system_prompt}\n\nExamples:\n{examples}\n\n{base.split('System:')[1]}"
