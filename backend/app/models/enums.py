import enum

class ProvenanceStatus(str, enum.Enum):
    AI_GENERATED = "AI_GENERATED"
    HUMAN_EDITED = "HUMAN_EDITED"
    HUMAN_CONFIRMED = "HUMAN_CONFIRMED"

class WeatherSensitivity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DayNight(str, enum.Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"
    DAWN = "DAWN"
    DUSK = "DUSK"
    EVENING = "EVENING"
    MORNING = "MORNING"
    CONTINUOUS = "CONTINUOUS"
    OTHER = "OTHER"

class LocationType(str, enum.Enum):
    INTERIOR = "INTERIOR"
    EXTERIOR = "EXTERIOR"
    INT_EXT = "INT_EXT"

class CharacterPresence(str, enum.Enum):
    APPEARS = "APPEARS"
    MENTIONED_ONLY = "MENTIONED_ONLY"
    VOICE_ONLY = "VOICE_ONLY"
    FLASHBACK = "FLASHBACK"
    DREAM = "DREAM"
    BACKGROUND = "BACKGROUND"
    CROWD = "CROWD"

class VehicleState(str, enum.Enum):
    ON_SCREEN = "ON_SCREEN"
    MOVING = "MOVING"
    PARKED = "PARKED"
    DRIVEN = "DRIVEN"
    BACKGROUND = "BACKGROUND"

class SpecialEffectCategory(str, enum.Enum):
    VFX = "VFX"
    SFX = "SFX"
    STUNT = "STUNT"
    ANIMAL = "ANIMAL"

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    EXTRACTING = "EXTRACTING"
    DETECTING_SCENES = "DETECTING_SCENES"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
