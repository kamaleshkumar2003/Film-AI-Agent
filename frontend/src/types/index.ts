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

// ==========================================
// V2 TYPES: PRODUCTION & SCHEDULING
// ==========================================

export type OptimizationProfile = 'BALANCED' | 'FASTEST' | 'CHEAPEST' | 'BEST_QUALITY';
export type ScheduleStatus = 'DRAFT' | 'OPTIMIZED' | 'LOCKED' | 'EXPORTED';
export type ConflictSeverity = 'INFO' | 'WARNING' | 'CRITICAL';
export type ConflictType =
  | 'CAST_UNAVAILABLE'
  | 'LOCATION_UNAVAILABLE'
  | 'MAX_HOURS_EXCEEDED'
  | 'WEATHER_MISMATCH'
  | 'LIGHTING_MISMATCH'
  | 'TURNAROUND_VIOLATION'
  | 'COMPANY_MOVE_EXCESSIVE'
  | 'CUSTOM';

export interface CastAvailability {
  id?: string;
  cast_member_id?: string;
  date: string;
  is_available: boolean;
  available_from?: string;
  available_to?: string;
  notes?: string;
}

export interface CastMember {
  id: string;
  project_id: string;
  name: string;
  character_name?: string;
  min_call_time?: string;
  max_hours_per_day: number;
  daily_rate: number;
  notes?: string;
  created_at?: string;
  availabilities: CastAvailability[];
}

export interface CrewAvailability {
  id?: string;
  crew_member_id?: string;
  date: string;
  is_available: boolean;
  available_from?: string;
  available_to?: string;
  notes?: string;
}

export interface CrewMember {
  id: string;
  project_id: string;
  name: string;
  role: string;
  max_hours_per_day: number;
  daily_rate: number;
  notes?: string;
  created_at?: string;
  availabilities: CrewAvailability[];
}

export interface LocationAvailability {
  id?: string;
  location_id?: string;
  date: string;
  is_available: boolean;
  available_from?: string;
  available_to?: string;
  notes?: string;
}

export interface ProductionLocation {
  id: string;
  project_id: string;
  name: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  location_type: LocationType;
  daily_rental_cost: number;
  opening_time: string;
  closing_time: string;
  setup_time_minutes: number;
  packup_time_minutes: number;
  notes?: string;
  created_at?: string;
  availabilities: LocationAvailability[];
}

export interface TravelMatrixItem {
  id?: string;
  project_id?: string;
  from_location_id: string;
  to_location_id: string;
  travel_time_minutes: number;
  distance_km?: number;
}

export interface ProductionConfig {
  id?: string;
  project_id: string;
  start_date: string;
  end_date: string;
  daily_start_time: string;
  daily_end_time: string;
  max_shooting_hours_per_day: number;
  lunch_duration_minutes: number;
  min_turnaround_hours: number;
  buffer_between_scenes_minutes: number;
  optimization_profile: OptimizationProfile;
  blackout_dates: string[];
  created_at?: string;
  updated_at?: string;
}

export interface ScheduleItem {
  id: string;
  shooting_day_id: string;
  scene_id: string;
  order_in_day: number;
  planned_start_time: string;
  planned_end_time: string;
  duration_minutes: number;
  location_id?: string;
  location_name?: string;
  company_move_before: boolean;
  travel_time_minutes_before: number;
  notes?: string;
  is_locked: boolean;
  scene?: SceneSummary;
}

export interface ShootingDay {
  id: string;
  schedule_version_id: string;
  day_number: number;
  date: string;
  primary_location_id?: string;
  primary_location_name?: string;
  call_time: string;
  wrap_time: string;
  total_shoot_minutes: number;
  overtime_minutes: number;
  weather_summary?: string;
  sunrise_time?: string;
  sunset_time?: string;
  notes?: string;
  items: ScheduleItem[];
}

export interface ScheduleConflict {
  id: string;
  schedule_version_id: string;
  scene_id?: string;
  conflict_type: ConflictType;
  severity: ConflictSeverity;
  message: string;
  details?: Record<string, any>;
}

export interface QualityScoreBreakdown {
  overall_score: number;
  location_grouping_score?: number;
  travel_minimization_score?: number;
  weather_compliance_score?: number;
  lighting_compliance_score?: number;
  overtime_score?: number;
  cast_continuity_score?: number;
  details?: Record<string, any>;
}

export interface ScheduleVersion {
  id: string;
  project_id: string;
  version_number: number;
  name: string;
  status: ScheduleStatus;
  objective_profile: OptimizationProfile;
  total_shooting_days: number;
  total_cost: number;
  quality_score: number;
  score_breakdown: QualityScoreBreakdown;
  explanation?: string;
  ai_review?: {
    strengths?: string[];
    potential_risks?: string[];
    contingency_recommendations?: string[];
  };
  created_at: string;
  shooting_days: ShootingDay[];
  conflicts: ScheduleConflict[];
}

export interface GenerateScheduleRequest {
  objective_profile?: OptimizationProfile;
  start_date?: string;
  end_date?: string;
  name?: string;
}

export interface MoveItemRequest {
  target_shooting_day_id: string;
  new_order: number;
}

export interface WhatIfRequest {
  scenario_type: 'cast_unavailable' | 'location_unavailable' | 'lose_day' | 'weather_delay';
  parameters: Record<string, any>;
}

export interface WhatIfResponse {
  feasible: boolean;
  message: string;
  hypothetical_days_count?: number;
  quality_score?: number;
  conflicts_count?: number;
  diff_summary?: string;
}

