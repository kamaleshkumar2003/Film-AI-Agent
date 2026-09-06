import httpx
from app.agents.base import BaseAIProvider
from app.schemas.breakdown import SceneBreakdownOutput
from app.agents.validator import BreakdownValidator
from app.prompts.breakdown_prompts import SYSTEM_BREAKDOWN_PROMPT, get_scene_user_prompt
from app.core.exceptions import AIAnalysisError
from app.core.logging import logger

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        self.api_key = api_key
        self.model_name = model_name

    async def analyze_scene(self, scene_heading: str, scene_text: str) -> SceneBreakdownOutput:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        prompt = f"{SYSTEM_BREAKDOWN_PROMPT}\n\n{get_scene_user_prompt(scene_heading, scene_text)}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
                return BreakdownValidator.validate_or_repair(raw_text)
        except Exception as e:
            logger.error(f"Gemini API analysis call failed: {str(e)}")
            raise AIAnalysisError(f"Gemini API analysis error: {str(e)}")
