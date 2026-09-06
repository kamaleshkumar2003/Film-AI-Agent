import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project, Screenplay, ProcessingJob
from app.models.scene import (
    Scene,
    SceneCharacter,
    SceneProp,
    SceneVehicle,
    SceneCostume,
    SceneMakeup,
    SceneCrewRequirement,
    SceneEquipment,
    SceneVFXStunts
)
from app.models.enums import JobStatus, ProvenanceStatus
from app.agents.factory import get_ai_provider
from app.core.logging import logger

class BreakdownService:
    @staticmethod
    async def run_breakdown_job(job_id: str, db_session_factory, force_reanalyze: bool = False):
        async with db_session_factory() as db:
            job_stmt = select(ProcessingJob).where(ProcessingJob.id == job_id)
            res = await db.execute(job_stmt)
            job = res.scalar_one_or_none()
            if not job:
                logger.error(f"Processing job {job_id} not found.")
                return

            try:
                job.status = JobStatus.ANALYZING
                job.current_step = "Loading detected scenes"
                await db.commit()

                scenes_stmt = select(Scene).where(Scene.project_id == job.project_id).order_by(Scene.scene_number)
                scenes_res = await db.execute(scenes_stmt)
                all_scenes = scenes_res.scalars().all()

                job.total_scenes = len(all_scenes)
                await db.commit()

                ai_provider = get_ai_provider()

                processed_count = 0
                for scene in all_scenes:
                    if not force_reanalyze and scene.confidence > 0.0:
                        chars_stmt = select(SceneCharacter).where(SceneCharacter.scene_id == scene.id)
                        c_res = await db.execute(chars_stmt)
                        if c_res.scalars().first():
                            processed_count += 1
                            job.processed_scenes = processed_count
                            await db.commit()
                            continue

                    job.current_step = f"Analyzing scene {scene.scene_number} of {len(all_scenes)}: {scene.scene_heading}"
                    await db.commit()

                    await BreakdownService._clear_scene_entities(db, scene.id)

                    breakdown_output = await ai_provider.analyze_scene(
                        scene_heading=scene.scene_heading,
                        scene_text=scene.raw_text
                    )

                    scene.location_name = breakdown_output.location.name
                    scene.int_ext = breakdown_output.location.location_type
                    scene.script_time = breakdown_output.time.script_time
                    scene.day_night = breakdown_output.time.day_night
                    scene.special_lighting = breakdown_output.time.special_lighting
                    scene.weather_sensitivity = breakdown_output.weather_sensitivity
                    scene.weather_reason = breakdown_output.weather_reason
                    scene.estimated_duration_minutes = breakdown_output.estimated_duration_minutes
                    scene.duration_confidence = breakdown_output.duration_confidence
                    scene.production_notes = "\n".join(breakdown_output.production_notes) if breakdown_output.production_notes else None
                    scene.continuity_notes = "\n".join(breakdown_output.continuity_notes) if breakdown_output.continuity_notes else None
                    scene.special_requirements = "\n".join(breakdown_output.special_requirements) if breakdown_output.special_requirements else None
                    scene.confidence = breakdown_output.confidence
                    scene.status = ProvenanceStatus.AI_GENERATED

                    for c in breakdown_output.characters:
                        db.add(SceneCharacter(
                            scene_id=scene.id,
                            name=c.name,
                            presence_type=c.presence_type,
                            description=c.description,
                            evidence=c.evidence,
                            confidence=c.confidence,
                            inferred=c.inferred,
                            reason=c.reason,
                            status=ProvenanceStatus.AI_GENERATED
                        ))

                    for p in breakdown_output.props:
                        db.add(SceneProp(
                            scene_id=scene.id,
                            name=p.name,
                            quantity=p.quantity,
                            is_required=p.is_required,
                            evidence=p.evidence,
                            confidence=p.confidence,
                            inferred=p.inferred,
                            reason=p.reason,
                            status=ProvenanceStatus.AI_GENERATED
                        ))

                    for v in breakdown_output.vehicles:
                        db.add(SceneVehicle(
                            scene_id=scene.id,
                            name=v.name,
                            vehicle_type=v.vehicle_type,
                            state=v.state,
                            evidence=v.evidence,
                            confidence=v.confidence,
                            inferred=v.inferred,
                            reason=v.reason,
                            status=ProvenanceStatus.AI_GENERATED
                        ))

                    for cost in breakdown_output.costumes:
                        db.add(SceneCostume(
                            scene_id=scene.id,
                            character_name=cost.character_name,
                            description=cost.description,
                            is_continuity=cost.is_continuity,
                            evidence=cost.evidence,
                            confidence=cost.confidence,
                            inferred=cost.inferred,
                            reason=cost.reason,
                            status=ProvenanceStatus.AI_GENERATED
                        ))

                    for mk in breakdown_output.makeup:
                        db.add(SceneMakeup(
                            scene_id=scene.id,
                            character_name=mk.character_name,
                            description=mk.description,
                            evidence=mk.evidence,
                            confidence=mk.confidence,
                            inferred=mk.inferred,
                            reason=mk.reason,
                            status=ProvenanceStatus.AI_GENERATED
                        ))

                    for cr in breakdown_output.crew_requirements:
                        db.add(SceneCrewRequirement(
                            scene_id=scene.id,
                            role=cr.role,
                            evidence=cr.evidence,
                            confidence=cr.confidence,
                            inferred=cr.inferred,
                            reason=cr.reason,
                            status=ProvenanceStatus.AI_GENERATED
                        ))

                    for eq in breakdown_output.equipment:
                        db.add(SceneEquipment(
                            scene_id=scene.id,
                            item_name=eq.item_name,
                            evidence=eq.evidence,
                            confidence=eq.confidence,
                            inferred=eq.inferred,
                            reason=eq.reason,
                            status=ProvenanceStatus.AI_GENERATED
                        ))

                    for vx in breakdown_output.vfx_stunts:
                        db.add(SceneVFXStunts(
                            scene_id=scene.id,
                            category=vx.category,
                            description=vx.description,
                            evidence=vx.evidence,
                            confidence=vx.confidence,
                            inferred=vx.inferred,
                            reason=vx.reason,
                            status=ProvenanceStatus.AI_GENERATED
                        ))

                    processed_count += 1
                    job.processed_scenes = processed_count
                    await db.commit()

                job.status = JobStatus.COMPLETED
                job.current_step = "Analysis complete"
                job.completed_at = datetime.datetime.now(datetime.timezone.utc)
                await db.commit()
                logger.info(f"Breakdown job {job_id} successfully completed {processed_count} scenes.")

            except Exception as e:
                logger.error(f"Breakdown job {job_id} failed: {str(e)}", exc_info=True)
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.current_step = f"Failed: {str(e)}"
                await db.commit()

    @staticmethod
    async def _clear_scene_entities(db: AsyncSession, scene_id: str):
        from sqlalchemy import delete
        await db.execute(delete(SceneCharacter).where(SceneCharacter.scene_id == scene_id))
        await db.execute(delete(SceneProp).where(SceneProp.scene_id == scene_id))
        await db.execute(delete(SceneVehicle).where(SceneVehicle.scene_id == scene_id))
        await db.execute(delete(SceneCostume).where(SceneCostume.scene_id == scene_id))
        await db.execute(delete(SceneMakeup).where(SceneMakeup.scene_id == scene_id))
        await db.execute(delete(SceneCrewRequirement).where(SceneCrewRequirement.scene_id == scene_id))
        await db.execute(delete(SceneEquipment).where(SceneEquipment.scene_id == scene_id))
        await db.execute(delete(SceneVFXStunts).where(SceneVFXStunts.scene_id == scene_id))
