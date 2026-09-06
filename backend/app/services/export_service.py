import io
import csv
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.scene import Scene

class ExportService:
    @staticmethod
    async def export_json(project_id: str, db: AsyncSession) -> Dict[str, Any]:
        proj_stmt = (
            select(Project)
            .options(
                selectinload(Project.scenes).selectinload(Scene.characters),
                selectinload(Project.scenes).selectinload(Scene.props),
                selectinload(Project.scenes).selectinload(Scene.vehicles),
                selectinload(Project.scenes).selectinload(Scene.costumes),
                selectinload(Project.scenes).selectinload(Scene.makeup),
                selectinload(Project.scenes).selectinload(Scene.crew_requirements),
                selectinload(Project.scenes).selectinload(Scene.equipment),
                selectinload(Project.scenes).selectinload(Scene.vfx_stunts)
            )
            .where(Project.id == project_id)
        )
        res = await db.execute(proj_stmt)
        project = res.scalar_one_or_none()
        if not project:
            return {}

        scenes_data = []
        for s in project.scenes:
            scenes_data.append({
                "scene_id": s.id,
                "scene_number": s.scene_number,
                "scene_code": s.scene_code,
                "scene_heading": s.scene_heading,
                "int_ext": s.int_ext.value if s.int_ext else None,
                "location_name": s.location_name,
                "day_night": s.day_night.value if s.day_night else None,
                "script_time": s.script_time,
                "special_lighting": s.special_lighting,
                "source_page_start": s.source_page_start,
                "source_page_end": s.source_page_end,
                "weather_sensitivity": s.weather_sensitivity.value if s.weather_sensitivity else "LOW",
                "weather_reason": s.weather_reason,
                "estimated_duration_minutes": s.estimated_duration_minutes,
                "duration_confidence": s.duration_confidence,
                "production_notes": s.production_notes,
                "continuity_notes": s.continuity_notes,
                "special_requirements": s.special_requirements,
                "status": s.status.value if s.status else "AI_GENERATED",
                "confidence": s.confidence,
                "characters": [
                    {
                        "name": c.name,
                        "presence_type": c.presence_type.value,
                        "description": c.description,
                        "evidence": c.evidence,
                        "confidence": c.confidence,
                        "inferred": c.inferred,
                        "reason": c.reason,
                        "status": c.status.value
                    } for c in s.characters
                ],
                "props": [
                    {
                        "name": p.name,
                        "quantity": p.quantity,
                        "is_required": p.is_required,
                        "evidence": p.evidence,
                        "confidence": p.confidence,
                        "inferred": p.inferred,
                        "reason": p.reason,
                        "status": p.status.value
                    } for p in s.props
                ],
                "vehicles": [
                    {
                        "name": v.name,
                        "vehicle_type": v.vehicle_type,
                        "state": v.state.value,
                        "evidence": v.evidence,
                        "confidence": v.confidence,
                        "inferred": v.inferred,
                        "reason": v.reason,
                        "status": v.status.value
                    } for v in s.vehicles
                ],
                "costumes": [
                    {
                        "character_name": cost.character_name,
                        "description": cost.description,
                        "is_continuity": cost.is_continuity,
                        "evidence": cost.evidence,
                        "confidence": cost.confidence,
                        "inferred": cost.inferred,
                        "reason": cost.reason,
                        "status": cost.status.value
                    } for cost in s.costumes
                ],
                "makeup": [
                    {
                        "character_name": mk.character_name,
                        "description": mk.description,
                        "evidence": mk.evidence,
                        "confidence": mk.confidence,
                        "inferred": mk.inferred,
                        "reason": mk.reason,
                        "status": mk.status.value
                    } for mk in s.makeup
                ],
                "crew_requirements": [
                    {
                        "role": cr.role,
                        "evidence": cr.evidence,
                        "confidence": cr.confidence,
                        "inferred": cr.inferred,
                        "reason": cr.reason,
                        "status": cr.status.value
                    } for cr in s.crew_requirements
                ],
                "equipment": [
                    {
                        "item_name": eq.item_name,
                        "evidence": eq.evidence,
                        "confidence": eq.confidence,
                        "inferred": eq.inferred,
                        "reason": eq.reason,
                        "status": eq.status.value
                    } for eq in s.equipment
                ],
                "vfx_stunts": [
                    {
                        "category": vx.category.value,
                        "description": vx.description,
                        "evidence": vx.evidence,
                        "confidence": vx.confidence,
                        "inferred": vx.inferred,
                        "reason": vx.reason,
                        "status": vx.status.value
                    } for vx in s.vfx_stunts
                ]
            })

        return {
            "project_id": project.id,
            "project_name": project.name,
            "production_type": project.production_type,
            "description": project.description,
            "director": project.director,
            "production_company": project.production_company,
            "scenes_count": len(scenes_data),
            "scenes": scenes_data
        }

    @staticmethod
    async def export_csv(project_id: str, db: AsyncSession) -> str:
        data = await ExportService.export_json(project_id, db)
        if not data or "scenes" not in data:
            return ""

        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            "Scene Number",
            "Scene Code",
            "Scene Heading",
            "INT/EXT",
            "Location",
            "Time",
            "Day/Night",
            "Pages",
            "Characters",
            "Props",
            "Vehicles",
            "Costumes",
            "Makeup",
            "Weather Sensitivity",
            "Weather Reason",
            "Estimated Duration (mins)",
            "Special Crew",
            "Special Requirements",
            "Status"
        ]
        writer.writerow(headers)

        for s in data["scenes"]:
            chars = "; ".join(f"{c['name']} ({c['presence_type']})" for c in s["characters"])
            props = "; ".join(f"{p['name']} (x{p['quantity']})" for p in s["props"])
            vehicles = "; ".join(f"{v['name']} [{v['state']}]" for v in s["vehicles"])
            costumes = "; ".join(c["description"] for c in s["costumes"])
            makeup = "; ".join(m["description"] for m in s["makeup"])
            crew = "; ".join(cr["role"] for cr in s["crew_requirements"])
            pages = f"{s['source_page_start']}-{s['source_page_end']}"

            writer.writerow([
                s["scene_number"],
                s["scene_code"],
                s["scene_heading"],
                s["int_ext"],
                s["location_name"],
                s["script_time"],
                s["day_night"],
                pages,
                chars,
                props,
                vehicles,
                costumes,
                makeup,
                s["weather_sensitivity"],
                s["weather_reason"] or "",
                s["estimated_duration_minutes"],
                crew,
                s["special_requirements"] or "",
                s["status"]
            ])

        return output.getvalue()
