class FilmPlannerException(Exception):
    """Base exception for film planner."""
    pass

class ScreenplayExtractionError(FilmPlannerException):
    """Raised when text extraction from screenplay fails."""
    pass

class SceneDetectionError(FilmPlannerException):
    """Raised when scene detection fails or encounters invalid formatting."""
    pass

class AIAnalysisError(FilmPlannerException):
    """Raised when AI analysis fails or schema validation fails after retry."""
    pass

class NotFoundError(FilmPlannerException):
    """Raised when an entity is not found."""
    pass
