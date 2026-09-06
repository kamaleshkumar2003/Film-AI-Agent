import json
import httpx
from app.agents.base import BaseAIProvider
from app.schemas.breakdown import SceneBreakdownOutput
from app.agents.validator import BreakdownValidator
from app.prompts.breakdown_prompts import SYSTEM_BREAKDOWN_PROMPT, get_scene_user_prompt
from app.core.exceptions import AIAnalysisError
from app.core.logging import logger

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    async def analyze_scene(self, scene_heading: str, scene_text: str) -> SceneBreakdownOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        schema = SceneBreakdownOutput.model_json_schema()
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_BREAKDOWN_PROMPT},
                {"role": "user", "content": get_scene_user_prompt(scene_heading, scene_text)}
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "scene_breakdown",
                    "strict": False,
                    "schema": schema
                }
            },
            "temperature": 0.1
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                raw_content = data["choices"][0]["message"]["content"]
                return BreakdownValidator.validate_or_repair(raw_content)
        except Exception as e:
            logger.error(f"OpenAI analysis call failed: {str(e)}")
            raise AIAnalysisError(f"OpenAI API analysis error: {str(e)}")
