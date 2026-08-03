"""
Smart College Assistant — IBM watsonx.ai LLM Wrapper
Provides a LangChain-compatible LLM using IBM Granite models.
Falls back to a mock LLM when credentials are not configured.
"""

from __future__ import annotations

import time
from typing import Any, Iterator

from utils.logger import get_ai_logger

logger = get_ai_logger()


# ── Mock LLM (fallback when IBM key is absent) ────────────────
class MockLLM:
    """
    Deterministic fallback LLM for development/testing without IBM credentials.
    Returns context-aware canned responses so the UI still works end-to-end.
    """

    def __init__(self, **kwargs):
        self.model_id = "mock-llm"
        logger.warning("IBM watsonx.ai not configured — using MockLLM fallback.")

    def invoke(self, prompt: str, **kwargs) -> str:
        return self._generate(str(prompt))

    def __call__(self, prompt: str, **kwargs) -> str:
        return self._generate(str(prompt))

    def _generate(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "admission" in prompt_lower:
            return (
                "Admission to our college involves the following steps: "
                "1) Fill the online application form on the college portal, "
                "2) Upload required documents (10th, 12th marksheets, TC, conduct certificate), "
                "3) Appear for the entrance examination, "
                "4) Attend the counseling session based on your rank, "
                "5) Pay the fee and confirm your seat. "
                "For more details, visit the Admissions section or call the helpdesk."
            )
        if any(w in prompt_lower for w in ["cgpa", "grade", "marks"]):
            return (
                "CGPA (Cumulative Grade Point Average) is calculated using the formula: "
                "CGPA = Σ(Grade Points × Credits) / Σ(Credits). "
                "Our college uses a 10-point grading scale: O=10, A+=9, A=8, B+=7, B=6, C=5, F=0. "
                "You can use the CGPA Calculator in the Smart Tools section."
            )
        if "placement" in prompt_lower:
            return (
                "Our Placement Cell coordinates with top companies for campus recruitment. "
                "The placement process includes: Pre-Placement Talk, Online Assessment, "
                "Technical Interview, and HR Interview. "
                "Eligibility: Minimum 6.0 CGPA with no active backlogs. "
                "Top recruiters include TCS, Infosys, Wipro, Cognizant, and more."
            )
        if any(w in prompt_lower for w in ["attendance", "absent"]):
            return (
                "The minimum attendance requirement is 75% in each subject. "
                "Students with 65%-74% attendance may apply for medical condonation. "
                "Students below 65% will be detained from examinations. "
                "Track your attendance in real-time from the Student Dashboard."
            )
        if any(w in prompt_lower for w in ["exam", "examination", "hall ticket"]):
            return (
                "End Semester Examinations are conducted twice a year. "
                "Hall tickets are available on the student portal 10 days before exams. "
                "Carry your hall ticket and college ID to every exam. "
                "Revaluation applications must be submitted within 15 days of results."
            )
        if "hostel" in prompt_lower:
            return (
                "Hostel facilities are available for both boys and girls separately. "
                "Fees: Single room – Rs. 45,000/year, Double sharing – Rs. 35,000/year. "
                "Includes meals, Wi-Fi, and round-the-clock security. "
                "In-time: 9:00 PM weekdays, 10:00 PM weekends."
            )
        if "scholarship" in prompt_lower:
            return (
                "Several scholarships are available: "
                "1) State Government Merit Scholarship for top performers, "
                "2) Central Sector Scholarship for income below Rs. 4.5L/year, "
                "3) SC/ST Scholarship through National Scholarship Portal, "
                "4) College Merit Scholarship for students in top 10%. "
                "Apply through the student portal during the announcement period."
            )
        if any(w in prompt_lower for w in ["hello", "hi", "hey", "help"]):
            return (
                "Hello! I'm the Smart College Assistant powered by IBM Granite AI. "
                "I can help you with: Admissions, Courses, Timetable, Attendance, "
                "Examinations, Placement Cell, College Policies, Scholarships, and more. "
                "What would you like to know today? 😊"
            )
        return (
            "Thank you for your question! I'm the Smart College Assistant. "
            "I can help you with admissions, academics, examinations, placements, "
            "attendance, policies, and much more. "
            "Could you please be more specific so I can give you the most accurate answer? "
            "You can also try the RAG Search to find information from uploaded college documents."
        )


# ── IBM watsonx.ai LLM Wrapper ───────────────────────────────
class WatsonxLLM:
    """
    LangChain-compatible wrapper for IBM watsonx.ai Granite models.

    Uses ibm-watsonx-ai SDK under the hood with proper error handling
    and request logging.
    """

    def __init__(
        self,
        model_id: str | None = None,
        api_key: str | None = None,
        project_id: str | None = None,
        url: str | None = None,
        max_new_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
    ):
        from config.settings import ActiveConfig

        self.model_id = model_id or ActiveConfig.IBM_MODEL_ID
        self.api_key = api_key or ActiveConfig.IBM_API_KEY
        self.project_id = project_id or ActiveConfig.IBM_PROJECT_ID
        self.url = url or ActiveConfig.IBM_URL
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self._model = None

        logger.info("Initializing WatsonxLLM with model: %s", self.model_id)
        self._init_model()

    def _init_model(self) -> None:
        """Initialize the IBM watsonx.ai model."""
        try:
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params

            creds = Credentials(url=self.url, api_key=self.api_key)
            params = {
                Params.DECODING_METHOD: "sample",
                Params.MAX_NEW_TOKENS: self.max_new_tokens,
                Params.TEMPERATURE: self.temperature,
                Params.TOP_P: self.top_p,
                Params.TOP_K: self.top_k,
                Params.REPETITION_PENALTY: 1.1,
            }
            self._model = ModelInference(
                model_id=self.model_id,
                credentials=creds,
                project_id=self.project_id,
                params=params,
            )
            logger.info("✅ IBM watsonx.ai model initialized: %s", self.model_id)

        except ImportError as e:
            logger.error("IBM watsonx-ai SDK not installed: %s", e)
            self._model = None
        except Exception as e:
            logger.error("Failed to initialize watsonx model: %s", e)
            self._model = None

    def invoke(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt string."""
        return self._call(str(prompt))

    def __call__(self, prompt: str, **kwargs) -> str:
        return self._call(str(prompt))

    def _call(self, prompt: str) -> str:
        """Internal call method with logging and error handling."""
        if self._model is None:
            logger.warning("Model unavailable; using fallback response.")
            return MockLLM()._generate(prompt)

        start = time.time()
        try:
            response = self._model.generate_text(prompt=prompt)
            elapsed = time.time() - start
            logger.info("IBM Granite response in %.2fs | Tokens: ~%d", elapsed, len(response.split()))
            return response.strip()
        except Exception as e:
            logger.error("watsonx.ai inference error: %s", e)
            return MockLLM()._generate(prompt)


def get_llm() -> WatsonxLLM | MockLLM:
    """
    Factory function — returns WatsonxLLM if configured, else MockLLM.

    Returns:
        LLM instance ready for use.
    """
    from config.settings import ActiveConfig

    if ActiveConfig.is_watsonx_configured():
        logger.info("IBM watsonx.ai credentials found — loading WatsonxLLM.")
        return WatsonxLLM()
    else:
        logger.warning("IBM credentials not set — using MockLLM.")
        return MockLLM()
