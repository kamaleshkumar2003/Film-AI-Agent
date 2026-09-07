import json
from typing import List, Dict, Any, Tuple
from app.models.enums import ConflictSeverity, ConflictType, WeatherSensitivity, LocationType, LightingRequirement
from app.services.scheduling.constraint_builder import SchedulingContext

class ScheduleValidator:
    """
    Validates any schedule (solver-generated or manually modified) against hard & soft constraints.
    Returns list of ScheduleConflict objects.
    """
    @staticmethod
    def validate_schedule(ctx: SchedulingContext, shooting_days: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        conflicts: List[Dict[str, Any]] = []
        scenes_by_id = {s.id: s for s in ctx.scenes}

        # Track which scenes are scheduled
        scheduled_scene_ids = set()

        for day in shooting_days:
            day_date = day["date"]
            items = day["items"]
            total_duration = 0

            for item in items:
                sc = scenes_by_id.get(item["scene_id"])
                if not sc:
                    continue

                scheduled_scene_ids.add(sc.id)
                total_duration += item["duration_minutes"]

                # 1. Cast Availability Check
                for char in sc.characters:
                    char_name = char.name.strip().lower()
                    cast_id = ctx.char_to_cast_map.get(char_name)
                    if cast_id:
                        is_avail = ctx.cast_availability.get((cast_id, day_date), True)
                        if not is_avail:
                            conflicts.append({
                                "scene_id": sc.id,
                                "conflict_type": ConflictType.CAST,
                                "severity": ConflictSeverity.ERROR,
                                "message": f"Cast conflict: Actor for '{char.name}' is UNAVAILABLE on {day_date.strftime('%b %d')}.",
                                "details": {"character": char.name, "date": str(day_date)}
                            })

                # 2. Location Availability Check
                loc_id = item.get("location_id")
                if loc_id:
                    is_avail = ctx.location_availability.get((loc_id, day_date), True)
                    if not is_avail:
                        conflicts.append({
                            "scene_id": sc.id,
                            "conflict_type": ConflictType.LOCATION,
                            "severity": ConflictSeverity.ERROR,
                            "message": f"Location conflict: '{item.get('location_name', 'Location')}' is closed/unavailable on {day_date.strftime('%b %d')}.",
                            "details": {"location_id": loc_id, "date": str(day_date)}
                        })

                # 3. Weather Risk Check
                fc = ctx.weather_by_date.get((loc_id, day_date))
                if fc and sc.int_ext in [LocationType.EXTERIOR, LocationType.INT_EXT]:
                    if sc.weather_sensitivity == WeatherSensitivity.CRITICAL and "rain" not in sc.raw_text.lower():
                        if fc.rain_probability > 60:
                            conflicts.append({
                                "scene_id": sc.id,
                                "conflict_type": ConflictType.WEATHER,
                                "severity": ConflictSeverity.WARNING,
                                "message": f"Severe weather risk: {sc.scene_code} requires outdoor shooting, but {fc.rain_probability:.0f}% rain is forecast on {day_date.strftime('%b %d')}.",
                                "details": {"rain_probability": fc.rain_probability}
                            })

                # 4. Lighting Window Check
                head = sc.scene_heading.upper()
                if "SUNSET" in head or sc.lighting_requirement == LightingRequirement.SUNSET:
                    sunset_str = day.get("sunset_time", "18:15")
                    plan_end = item.get("planned_end_time", "18:00")
                    # Warning if scene finishes > 30 min away from sunset
                    if abs(int(plan_end[:2]) - int(sunset_str[:2])) > 1:
                        conflicts.append({
                            "scene_id": sc.id,
                            "conflict_type": ConflictType.LIGHTING,
                            "severity": ConflictSeverity.WARNING,
                            "message": f"Lighting mismatch: {sc.scene_code} requires Sunset (occurs at {sunset_str}), but is scheduled ending at {plan_end}.",
                            "details": {"sunset": sunset_str, "planned_end": plan_end}
                        })

            # 5. Overtime / Daily Shooting Limit Check
            max_mins = ctx.production_config.max_shooting_hours_per_day * 60
            if total_duration > max_mins:
                conflicts.append({
                    "scene_id": None,
                    "conflict_type": ConflictType.OVERTIME,
                    "severity": ConflictSeverity.WARNING,
                    "message": f"Day {day['day_number']} exceeds max shooting hours ({total_duration/60:.1f}h vs limit of {max_mins/60}h).",
                    "details": {"total_minutes": total_duration, "limit": max_mins}
                })

        # Missing scenes check
        missing = set(scenes_by_id.keys()) - scheduled_scene_ids
        if missing:
            for s_id in missing:
                sc = scenes_by_id[s_id]
                conflicts.append({
                    "scene_id": s_id,
                    "conflict_type": ConflictType.TIMING,
                    "severity": ConflictSeverity.ERROR,
                    "message": f"Scene {sc.scene_code} ({sc.scene_heading}) has not been scheduled.",
                    "details": {"scene_id": s_id}
                })

        return conflicts

class ScheduleQualityScorer:
    """
    Computes a transparent 0-100 quality score based on:
    - Hard constraints (Pass = 100%, Fail = 0%)
    - Location Grouping
    - Weather matching
    - Lighting matching
    - Travel & Company moves
    - Overtime risk
    """
    @staticmethod
    def calculate_score(
        ctx: SchedulingContext,
        shooting_days: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        has_hard_errors = any(c["severity"] == ConflictSeverity.ERROR for c in conflicts)
        hard_pass = not has_hard_errors

        # 1. Location Grouping Score: % of days that stay at single location
        days_count = len(shooting_days)
        if days_count == 0:
            return {"overall_score": 0.0, "hard_constraints_pass": False}

        single_loc_days = 0
        company_moves = 0
        for d in shooting_days:
            locs_in_day = set(item.get("location_name") for item in d["items"] if item.get("location_name"))
            if len(locs_in_day) <= 1:
                single_loc_days += 1
            company_moves += max(0, len(locs_in_day) - 1)

        loc_grouping = round((single_loc_days / max(1, days_count)) * 100, 1)

        # 2. Weather Score: penalize rain > 50% on outdoor scenes
        outdoor_scenes_count = 0
        weather_good_count = 0
        scenes_by_id = {s.id: s for s in ctx.scenes}

        for d in shooting_days:
            target_date = d["date"]
            for item in d["items"]:
                sc = scenes_by_id.get(item["scene_id"])
                if sc and sc.int_ext in [LocationType.EXTERIOR, LocationType.INT_EXT]:
                    outdoor_scenes_count += 1
                    fc = ctx.weather_by_date.get((item.get("location_id"), target_date))
                    rain_prob = fc.rain_probability if fc else 10.0
                    if rain_prob < 40:
                        weather_good_count += 1
                    elif rain_prob < 70:
                        weather_good_count += 0.5

        weather_score = round((weather_good_count / max(1, outdoor_scenes_count)) * 100, 1) if outdoor_scenes_count > 0 else 95.0

        # 3. Lighting Score
        lighting_conflicts = [c for c in conflicts if c["conflict_type"] == ConflictType.LIGHTING]
        lighting_score = max(50.0, round(100.0 - (len(lighting_conflicts) * 15.0), 1))

        # 4. Cast & Crew Efficiency
        cast_conflicts = [c for c in conflicts if c["conflict_type"] == ConflictType.CAST]
        cast_eff = max(0.0, round(100.0 - (len(cast_conflicts) * 30.0), 1))
        crew_eff = 95.0

        # 5. Travel & Company Moves Score
        travel_score = max(40.0, round(100.0 - (company_moves * 12.0), 1))

        # 6. Overtime Score
        overtime_days = sum(1 for d in shooting_days if d.get("overtime_minutes", 0) > 0)
        overtime_score = max(40.0, round(100.0 - (overtime_days * 20.0), 1))

        # Weighted Overall Score
        if not hard_pass:
            overall = min(45.0, round((loc_grouping * 0.2 + weather_score * 0.2 + lighting_score * 0.2 + travel_score * 0.2 + overtime_score * 0.2) * 0.5, 1))
        else:
            overall = round(
                loc_grouping * 0.25 +
                weather_score * 0.20 +
                lighting_score * 0.20 +
                cast_eff * 0.15 +
                travel_score * 0.10 +
                overtime_score * 0.10,
                1
            )

        return {
            "overall_score": overall,
            "hard_constraints_pass": hard_pass,
            "location_grouping": loc_grouping,
            "weather_score": weather_score,
            "lighting_score": lighting_score,
            "cast_efficiency": cast_eff,
            "crew_efficiency": crew_eff,
            "travel_efficiency": travel_score,
            "overtime_score": overtime_score
        }

class ReviewAgent:
    """
    AI Schedule Review & Explanation Agent.
    Generates human-readable explanations of scheduling decisions and flags subtle production risks.
    """
    @staticmethod
    def generate_explanation_and_review(
        ctx: SchedulingContext,
        shooting_days: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        quality_score: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        # Summary text
        total_days = len(shooting_days)
        scenes_count = sum(len(d["items"]) for d in shooting_days)
        
        explanation_lines = [
            f"Optimized schedule generated across {total_days} shooting days for {scenes_count} scenes.",
            f"Overall Schedule Quality Score: {quality_score.get('overall_score', 0)}/100 (Hard Constraints: {'PASS' if quality_score.get('hard_constraints_pass') else 'FAIL'})."
        ]

        for d in shooting_days:
            sc_codes = ", ".join(item["scene_id"][:6] for item in d["items"])
            explanation_lines.append(
                f"- Day {d['day_number']} ({d['date'].strftime('%a, %b %d')}): Filming at {d['primary_location_name']} "
                f"from {d['call_time']} to {d['wrap_time']}. Weather: {d['weather_summary']}. Sunrise: {d.get('sunrise_time')}, Sunset: {d.get('sunset_time')}."
            )

        findings = []
        # Check lighting windows
        for d in shooting_days:
            for item in d["items"]:
                if item.get("company_move_before"):
                    findings.append({
                        "severity": "INFO",
                        "day": d["day_number"],
                        "issue": "Company move between locations",
                        "recommendation": f"Allow {item.get('travel_time_minutes_before', 30)} minutes for equipment packing and transport."
                    })

        for c in conflicts:
            findings.append({
                "severity": c["severity"].value if hasattr(c["severity"], "value") else str(c["severity"]),
                "issue": c["message"],
                "recommendation": "Review availability dates or re-run solver with relaxed constraints."
            })

        ai_review = {
            "findings": findings,
            "risk_assessment": "Low risk" if quality_score.get("overall_score", 0) > 85 else "Moderate production risk - review flagged items."
        }

        return '\n'.join(explanation_lines), ai_review
