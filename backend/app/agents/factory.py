from app.config import settings
from app.agents.base import BaseAIProvider
from app.agents.mock_provider import MockAIProvider
from app.agents.openai_provider import OpenAIProvider
from app.agents.gemini_provider import GeminiProvider
from app.core.logging import logger

def get_ai_provider() -> BaseAIProvider:
    provider = settings.AI_PROVIDER.lower()
    
    if provider == "openai" and settings.OPENAI_API_KEY:
        logger.info("Using OpenAI AI Provider")
        return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model_name=settings.AI_MODEL_NAME)
    elif provider == "gemini" and settings.GEMINI_API_KEY:
        logger.info("Using Google Gemini AI Provider")
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.AI_MODEL_NAME)
    else:
        logger.info("Using High-Fidelity Heuristic AI Provider")
        return MockAIProvider()
