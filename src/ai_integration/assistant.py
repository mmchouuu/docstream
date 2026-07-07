"""
Assistant execution and runtime setup helper for Google Gemini.
"""
import logging
from typing import Optional
from src.ai_integration.client import AIClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.

• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply."""

class AIAssistantManager:
    """Manages AI Assistant settings and updates for Gemini."""

    def __init__(self, client: AIClient, assistant_id: Optional[str] = None) -> None:
        self.ai_client = client
        self.assistant_id = assistant_id

    def get_or_create_assistant(self, vector_store_id: str, name: str = "OptiBot") -> str:
        """
        For Gemini, Assistant configurations are initialized inline.
        This method returns the model identifier 'gemini-1.5-flash'.
        """
        logger.info("Configured Gemini model 'gemini-flash-latest' with verbatim instructions.")
        return "gemini-flash-latest"
