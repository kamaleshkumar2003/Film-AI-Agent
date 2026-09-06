from abc import ABC, abstractmethod
from app.schemas.breakdown import SceneBreakdownOutput

class BaseAIProvider(ABC):
    @abstractmethod
    async def analyze_scene(self, scene_heading: str, scene_text: str) -> SceneBreakdownOutput:
        """Analyze a single scene and return structured validated breakdown."""
        pass
