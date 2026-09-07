from pathlib import Path

solver_code = '''import datetime
from typing import List, Dict, Any, Tuple
from ortools.sat.python import cp_model
from app.models.enums import (
    OptimizationProfile, WeatherSensitivity, LightingRequirement, LocationType
)
from app.services.scheduling.constraint_builder import SchedulingContext

class CPSATScheduler:
    def __init__(self, context: SchedulingContext, profile: OptimizationProfile = OptimizationProfile.BALANCED):
        self.ctx = context
        self.profile = profile
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = 15.0 # fast, deterministic solve

    def solve(self) -> Dict[str, Any]:
        scenes = self.ctx.scenes
        dates = self.ctx.candidate_dates
        num_scenes = len(scenes)
        num_dates = len(dates)

        if num_scenes == 0 or num_dates == 0:
            return {"status": "EMPTY", "days": []}

        # 1. Decision variables: x[s, d] == 1 iff scene s is shot on date d
        x = {}
        for s in range(num_scenes):
            for d in range(num_dates):
                x[s, d] = self.model.NewBoolVar(f"scene_{s}_day_{d}")

        # day_used[d] == 1 iff day d has at least one scene
        day_used = {}
        for d in range(num_dates):
            day_used[d] = self.model.NewBoolVar(f"day_used_{d}")

        # day_location[d, loc_id] == 1 iff loc_id is visited on day d
        locations = self.ctx.locations or []
        day_loc = {}
        for d in range(num_dates):
            for loc in locations:
                day_loc[d, loc.id] = self.model.NewBoolVar(f"day_{d}_loc_{loc.id}")

        # --- HARD CONSTRAINTS ---

        # (a) Every scene must be assigned to EXACTLY ONE day
        for s in range(num_scenes):
            self.model.Add(sum(x[s, d] for d in range(num_dates)) == 1)

        # (b) Link day_used with scenes
        for d in range(num_dates):
            self.model.Add(sum(x[s, d] for s in range(num_scenes)) <= num_scenes * day_used[d])
            self.model.Add(sum(x[s, d] for s in range(num_scenes)) >= day_used[d])

        # (c) Link day_loc with scenes
        for s, scene in enumerate(scenes):
            loc_id = self._get_scene_location_id(scene)
            if loc_id and loc_id in [l.id for l in locations]:
                for d in range(num_dates):
                    self.model.Add(x[s, d] <= day_loc[d, loc_id])

        # (d) Maximum shooting hours per day
        max_minutes = self.ctx.production_config.max_shooting_hours_per_day * 60
        for d in range(num_dates):
            day_durations = [
                x[s, d] * scenes[s].effective_duration_minutes
                for s in range(num_scenes)
            ]
            self.model.Add(sum(day_durations) <= max_minutes)

        # (e) Cast Availability (HARD CONSTRAINT)
        for s, scene in enumerate(scenes):
            for char in scene.characters:
                char_name = char.name.strip().lower()
                cast_id = self.ctx.char_to_cast_map.get(char_name)
                if cast_id:
                    for d, target_date in enumerate(dates):
                        is_avail = self.ctx.cast_availability.get((cast_id, target_date), True)
                        if not is_avail:
                            self.model.Add(x[s, d] == 0)

        # (f) Location Availability (HARD CONSTRAINT)
        for s, scene in enumerate(scenes):
            loc_id = self._get_scene_location_id(scene)
            if loc_id:
                for d, target_date in enumerate(dates):
                    is_avail = self.ctx.location_availability.get((loc_id, target_date), True)
                    if not is_avail:
                        self.model.Add(x[s, d] == 0)

        # (g) Manual Scene Locks (HARD CONSTRAINT)
        for s, scene in enumerate(scenes):
            if scene.is_locked and scene.locked_day_number is not None:
                day_idx = scene.locked_day_number - 1
                if 0 <= day_idx < num_dates:
                    self.model.Add(x[s, day_idx] == 1)

        # --- SOFT CONSTRAINTS & WEIGHTED OBJECTIVE ---
        objective_terms = []

        # Weights based on Profile
        w_days = 500
        w_moves = 250
        w_weather = 150
        w_lighting = 200

        if self.profile == OptimizationProfile.FASTEST:
            w_days = 1500
            w_moves = 100
        elif self.profile == OptimizationProfile.CHEAPEST:
            w_days = 300
            w_moves = 600
        elif self.profile == OptimizationProfile.BEST_QUALITY:
            w_weather = 400
            w_lighting = 500

        # 1. Minimize total shooting days
        for d in range(num_dates):
            objective_terms.append(-w_days * day_used[d])

        # 2. Minimize company moves (multiple locations in same day)
        for d in range(num_dates):
            if locations:
                loc_count_on_day = sum(day_loc[d, loc.id] for loc in locations)
                # penalty for each location beyond the first on day d
                objective_terms.append(-w_moves * loc_count_on_day)

        # 3. Weather sensitivity penalty
        for s, scene in enumerate(scenes):
            loc_id = self._get_scene_location_id(scene)
            is_ext = scene.int_ext in [LocationType.EXTERIOR, LocationType.INT_EXT]
            for d, target_date in enumerate(dates):
                fc = self.ctx.weather_by_date.get((loc_id, target_date))
                rain_prob = fc.rain_probability if fc else 10.0

                if is_ext:
                    if scene.weather_sensitivity == WeatherSensitivity.CRITICAL and "rain" in (scene.raw_text.lower()):
                        # Scene actually requires rain! Reward rainy days
                        if rain_prob > 50:
                            objective_terms.append(w_weather * x[s, d])
                    else:
                        # Outdoor scene: penalize rain
                        if rain_prob > 40:
                            penalty = int(w_weather * (rain_prob / 100.0))
                            objective_terms.append(-penalty * x[s, d])

        # 4. Lighting matching
        for s, scene in enumerate(scenes):
            loc_id = self._get_scene_location_id(scene)
            req = scene.lighting_requirement
            head = scene.scene_heading.upper()
            is_sunset = req == LightingRequirement.SUNSET or "SUNSET" in head or "DUSK" in head
            is_dawn = req in [LightingRequirement.DAWN, LightingRequirement.SUNRISE] or "DAWN" in head or "SUNRISE" in head

            for d, target_date in enumerate(dates):
                if is_sunset or is_dawn:
                    # Reward scheduling lighting scenes on days with clear skies (<30% rain)
                    fc = self.ctx.weather_by_date.get((loc_id, target_date))
                    rain_prob = fc.rain_probability if fc else 10.0
                    if rain_prob <= 25:
                        objective_terms.append(w_lighting * x[s, d])

        self.model.Maximize(sum(objective_terms))

        # Solve
        status = self.solver.Solve(self.model)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return {
                "status": "INFEASIBLE",
                "days": [],
                "error": "No valid schedule exists that satisfies all hard constraints (cast availability, location availability, or max hours)."
            }

        # Format days & sequence scenes
        scheduled_days = []
        active_day_num = 1

        for d, target_date in enumerate(dates):
            if self.solver.Value(day_used[d]) == 1:
                day_scenes = [scenes[s] for s in range(num_scenes) if self.solver.Value(x[s, d]) == 1]
                if not day_scenes:
                    continue

                sequenced_items = self._sequence_day_scenes(day_scenes, target_date)
                
                # Primary location for day
                prim_loc = day_scenes[0].location_name
                loc_id = self._get_scene_location_id(day_scenes[0])
                fc = self.ctx.weather_by_date.get((loc_id, target_date))
                lw = self.ctx.lighting_by_date.get((loc_id, target_date), {})

                weather_summary = f"{fc.condition}, {fc.temperature_c}°C, Rain {fc.rain_probability:.0f}%" if fc else "Clear Sky, 28°C"
                call_time = sequenced_items[0]["planned_start_time"] if sequenced_items else "06:00"
                wrap_time = sequenced_items[-1]["planned_end_time"] if sequenced_items else "18:00"
                total_mins = sum(item["duration_minutes"] for item in sequenced_items)

                scheduled_days.append({
                    "day_number": active_day_num,
                    "date": target_date,
                    "primary_location_id": loc_id,
                    "primary_location_name": prim_loc,
                    "call_time": call_time,
                    "wrap_time": wrap_time,
                    "total_shoot_minutes": total_mins,
                    "overtime_minutes": max(0, total_mins - (self.ctx.production_config.max_shooting_hours_per_day * 60)),
                    "weather_summary": weather_summary,
                    "sunrise_time": lw.get("sunrise", "06:00"),
                    "sunset_time": lw.get("sunset", "18:15"),
                    "items": sequenced_items
                })
                active_day_num += 1

        return {
            "status": "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE",
            "days": scheduled_days
        }

    def _get_scene_location_id(self, scene: Scene) -> Optional[str]:
        if scene.locked_location_id:
            return scene.locked_location_id
        return self.ctx.scene_loc_to_prod_loc.get(scene.location_name.strip().lower())

    def _sequence_day_scenes(self, scenes: List[Scene], target_date: datetime.date) -> List[Dict[str, Any]]:
        # Order scenes logically:
        # 1. DAWN / SUNRISE scenes first
        # 2. Group by location
        # 3. Regular DAY scenes
        # 4. SUNSET / GOLDEN_HOUR scenes near sunset
        # 5. NIGHT scenes after sunset
        def sort_key(s: Scene):
            head = s.scene_heading.upper()
            if "DAWN" in head or "SUNRISE" in head or s.lighting_requirement in [LightingRequirement.DAWN, LightingRequirement.SUNRISE]:
                return (0, s.location_name, s.scene_number)
            elif "NIGHT" in head or s.lighting_requirement == LightingRequirement.NORMAL_NIGHT:
                return (4, s.location_name, s.scene_number)
            elif "SUNSET" in head or "DUSK" in head or s.lighting_requirement == LightingRequirement.SUNSET:
                return (3, s.location_name, s.scene_number)
            else:
                return (1, s.location_name, s.scene_number)

        ordered = sorted(scenes, key=sort_key)

        items = []
        # Start at configured call time
        start_dt = datetime.datetime.combine(target_date, datetime.time(6, 30))
        current_time = start_dt
        prev_loc_id = None

        for idx, sc in enumerate(ordered):
            loc_id = self._get_scene_location_id(sc)
            company_move = False
            travel_mins = 0

            # Check company move
            if prev_loc_id and loc_id and prev_loc_id != loc_id:
                company_move = True
                travel_mins = self.ctx.travel_times.get((prev_loc_id, loc_id), 30)
                current_time += datetime.timedelta(minutes=travel_mins)

            dur = sc.effective_duration_minutes
            start_str = current_time.strftime("%H:%M")
            end_time = current_time + datetime.timedelta(minutes=dur)
            end_str = end_time.strftime("%H:%M")

            items.append({
                "scene_id": sc.id,
                "order_in_day": idx + 1,
                "planned_start_time": start_str,
                "planned_end_time": end_str,
                "duration_minutes": dur,
                "location_id": loc_id,
                "location_name": sc.location_name,
                "company_move_before": company_move,
                "travel_time_minutes_before": travel_mins,
                "is_locked": sc.is_locked,
                "notes": sc.production_notes
            })

            # Buffer between scenes: 15 mins
            current_time = end_time + datetime.timedelta(minutes=self.ctx.production_config.buffer_between_scenes_minutes)
            prev_loc_id = loc_id

        return items
'''
Path("backend/app/services/scheduling/cp_sat_solver.py").write_text(solver_code, encoding="utf-8")
print("CPSATScheduler created.")
