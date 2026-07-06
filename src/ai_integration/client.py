"""
Low-level client wrapper for the target AI platform API (e.g. OpenAI or Gemini).
"""
class AIClient:
    """Wrapper class around AI SDK endpoints."""
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
