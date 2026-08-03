"""Smart College Assistant — Timetable Agent"""
from agents.base_agent import BaseAgent
from prompts.system_prompts import TIMETABLE_SYSTEM_PROMPT


class TimetableAgent(BaseAgent):
    """Handles timetable and schedule queries."""
    name = "timetable_agent"
    system_prompt = TIMETABLE_SYSTEM_PROMPT
