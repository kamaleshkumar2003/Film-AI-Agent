export type ProvenanceStatus = 'AI_GENERATED' | 'HUMAN_EDITED' | 'HUMAN_CONFIRMED';
export type WeatherSensitivity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type DayNight = 'DAY' | 'NIGHT' | 'DAWN' | 'DUSK' | 'EVENING' | 'MORNING' | 'CONTINUOUS' | 'OTHER';
export type LocationType = 'INTERIOR' | 'EXTERIOR' | 'INT_EXT';
export type CharacterPresence = 'APPEARS' | 'MENTIONED_ONLY' | 'VOICE_ONLY' | 'FLASHBACK' | 'DREAM' | 'BACKGROUND' | 'CROWD';
export type VehicleState = 'ON_SCREEN' | 'MOVING' | 'PARKED' | 'DRIVEN' | 'BACKGROUND';
export type SpecialEffectCategory = 'VFX' | 'SFX' | 'STUNT' | 'ANIMAL';
export type JobStatus = 'PENDING' | 'EXTRACTING' | 'DETECTING_SCENES' | 'ANALYZING' | 'COMPLETED' | 'FAILED';

export interface Screenplay {
  id: string;
  project_id: string;
  filename: string;
  file_format: string;
  file_size_bytes: number;
  page_count: number;
  version: number;
  uploaded_at: string;
}

export interface ProjectStats {
  total_scenes: number;
  analyzed_scenes: number;
  total_characters: number;
  total_locations: number;
  total_props: number;
  total_vehicles: number;
  critical_weather_scenes: number;
}

export interface Project {
  id: string;
  name: string;
  production_type: string;
  description?: string;
  director?: string;
  production_company?: string;
  created_at: string;
  updated_at: string;
  screenplays: Screenplay[];
  stats?: ProjectStats;
}

export interface SceneSummary {
  id: string;
  project_id: string;
  scene_number: number;
  scene_code: string;
  scene_heading: string;
  int_ext: LocationType;
  location_name: string;
  day_night: DayNight;
  script_time: string;
  special_lighting?: string;
  source_page_start: number;
  source_page_end: number;
  weather_sensitivity: WeatherSensitivity;
  estimated_duration_minutes: number;
  status: ProvenanceStatus;
  confidence: number;
  character_count: number;
  prop_count: number;
  vehicle_count: number;
  character_names: string[];
}

export interface SceneCharacter {
  id: string;
  scene_id: string;
  name: string;
  presence_type: CharacterPresence;
  description?: string;
  evidence?: string;
  confidence: number;
  inferred: boolean;
  reason?: string;
  status: ProvenanceStatus;
}

export interface SceneProp {
  id: string;
  scene_id: string;
  name: string;
  quantity: number;
  is_required: boolean;
  evidence?: string;
  confidence: number;
  inferred: boolean;
  reason?: string;
  status: ProvenanceStatus;
}

export interface SceneVehicle {
  id: string;
  scene_id: string;
  name: string;
  vehicle_type: string;
  state: VehicleState;
  evidence?: string;
  confidence: number;
  inferred: boolean;
  reason?: string;
  status: ProvenanceStatus;
}

export interface SceneCostume {
  id: string;
  scene_id: string;
  character_name?: string;
  description: string;
  is_continuity: boolean;
  evidence?: string;
  confidence: number;
  inferred: boolean;
  reason?: string;
  status: ProvenanceStatus;
}

export interface SceneMakeup {
  id: string;
  scene_id: string;
  character_name?: string;
  description: string;
  evidence?: string;
  confidence: number;
  inferred: boolean;
  reason?: string;
  status: ProvenanceStatus;
}

export interface SceneCrewRequirement {
  id: string;
  scene_id: string;
  role: string;
  evidence?: string;
  confidence: number;
  inferred: boolean;
  reason?: string;
  status: ProvenanceStatus;
}

export interface SceneEquipment {
  id: string;
  scene_id: string;
  item_name: string;
  evidence?: string;
  confidence: number;
  inferred: boolean;
  reason?: string;
  status: ProvenanceStatus;
}

export interface SceneVFXStunt {
  id: string;
  scene_id: string;
  category: SpecialEffectCategory;
  description: string;
  evidence?: string;
  confidence: number;
  inferred: boolean;
  reason?: string;
  status: ProvenanceStatus;
}

export interface SceneDetail extends SceneSummary {
  screenplay_id?: string;
  raw_text: string;
  weather_reason?: string;
  duration_confidence: number;
  production_notes?: string;
  continuity_notes?: string;
  special_requirements?: string;
  created_at: string;
  updated_at: string;
  characters: SceneCharacter[];
  props: SceneProp[];
  vehicles: SceneVehicle[];
  costumes: SceneCostume[];
  makeup: SceneMakeup[];
  crew_requirements: SceneCrewRequirement[];
  equipment: SceneEquipment[];
  vfx_stunts: SceneVFXStunt[];
}

export interface JobResponse {
  id: string;
  project_id: string;
  screenplay_id?: string;
  status: JobStatus;
  current_step: string;
  total_scenes: number;
  processed_scenes: number;
  error_message?: string;
  started_at: string;
  completed_at?: string;
  progress_percentage: number;
}
