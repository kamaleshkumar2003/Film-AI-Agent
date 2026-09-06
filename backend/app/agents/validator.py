import json
import re
from typing import Any, Dict
from pydantic import ValidationError
from app.schemas.breakdown import SceneBreakdownOutput
from app.core.exceptions import AIAnalysisError
from app.core.logging import logger

class BreakdownValidator:
    @staticmethod
    def validate_or_repair(raw_output: Any) -> SceneBreakdownOutput:
        if isinstance(raw_output, SceneBreakdownOutput):
            return raw_output

        data: Dict[str, Any] = {}
        if isinstance(raw_output, str):
            clean_str = raw_output.strip()
            if clean_str.startswith("```"):
                clean_str = re.sub(r"^```(?:json)?\s*", "", clean_str)
                clean_str = re.sub(r"\s*```$", "", clean_str)
            try:
                data = json.loads(clean_str)
            except json.JSONDecodeError as e:
                match = re.search(r"(\{.*\})", clean_str, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                    except Exception:
                        raise AIAnalysisError(f"Malformed JSON from AI model: {str(e)}")
                else:
                    raise AIAnalysisError(f"Malformed JSON from AI model: {str(e)}")
        elif isinstance(raw_output, dict):
            data = raw_output
        else:
            raise AIAnalysisError(f"Unexpected AI output type: {type(raw_output)}")

        try:
            return SceneBreakdownOutput.model_validate(data)
        except ValidationError as val_err:
            logger.warning(f"Schema validation error, attempting default coercion: {val_err}")
            if "location" not in data or not isinstance(data["location"], dict):
                data["location"] = {"name": "Location", "location_type": "INTERIOR"}
            if "time" not in data or not isinstance(data["time"], dict):
                data["time"] = {"script_time": "DAY", "day_night": "DAY"}
            if "scene_heading" not in data:
                data["scene_heading"] = "SCENE"
            try:
                return SceneBreakdownOutput.model_validate(data)
            except ValidationError as final_err:
                raise AIAnalysisError(f"Failed to validate breakdown schema: {final_err}")
