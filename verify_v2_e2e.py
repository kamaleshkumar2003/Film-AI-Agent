import asyncio
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from app.core.database import init_db
from app.main import app

async def run_v2_e2e_verification():
    print("=== STARTING FULL V2 END-TO-END VERIFICATION ===")
    await init_db()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as client:
        # 1. Health check (Verify V2)
        h_res = await client.get("/health")
        assert h_res.status_code == 200, f"Health check failed: {h_res.text}"
        h_data = h_res.json()
        assert h_data["version"] == "2.0.0", f"Expected version 2.0.0, got {h_data['version']}"
        print(f"[OK] 1. Backend Health Check OK: Version {h_data['version']}")

        # 2. Create Project
        p_res = await client.post("/api/projects", json={
            "name": "Project Neon Harbor V2",
            "production_type": "Feature Film",
            "director": "Christopher Nolan",
            "production_company": "Syncopy",
            "description": "High-stakes neo-noir thriller set across neon-lit harbor and warehouses."
        })
        assert p_res.status_code == 201
        project = p_res.json()
        project_id = project["id"]
        print(f"[OK] 2. Created Project: {project['name']} (ID: {project_id})")

        # 3. Upload neon_harbor.txt screenplay
        screenplay_path = Path("backend/sample_screenplays/neon_harbor.txt")
        file_bytes = screenplay_path.read_bytes()
        up_res = await client.post(
            f"/api/projects/{project_id}/screenplay",
            files={"file": ("neon_harbor.txt", file_bytes, "text/plain")}
        )
        assert up_res.status_code == 200
        print(f"[OK] 3. Screenplay Uploaded: {up_res.json()['scenes_detected']} scenes detected")

        # 4. Trigger AI Breakdown Job & Poll
        job_res = await client.post(f"/api/projects/{project_id}/analyze")
        assert job_res.status_code == 200
        job_id = job_res.json()["id"]
        
        for _ in range(30):
            await asyncio.sleep(0.4)
            st_res = await client.get(f"/api/jobs/{job_id}")
            if st_res.json()["status"] in ["COMPLETED", "FAILED"]:
                break
        assert st_res.json()["status"] == "COMPLETED"
        print(f"[OK] 4. AI Breakdown Completed: {st_res.json()['processed_scenes']} scenes analyzed")

        # 5. One-Click Demo Seed (Locations, Travel Matrix, Cast, Crew, Blackout Dates)
        seed_res = await client.post(f"/api/projects/{project_id}/schedule/demo-seed")
        assert seed_res.status_code == 200
        seed_data = seed_res.json()
        print(f"[OK] 5. Demo Seeded: {seed_data['locations_created']} locations, {seed_data['cast_created']} cast, {seed_data['crew_created']} crew. Constraint: {seed_data['test_constraint']}")

        # Verify Cast List
        cast_res = await client.get(f"/api/projects/{project_id}/cast")
        assert cast_res.status_code == 200
        cast_list = cast_res.json()
        assert len(cast_list) == 4
        print(f"   Cast roster verified: {', '.join(c['name'] for c in cast_list)}")

        # Verify Locations & Travel Matrix
        loc_res = await client.get(f"/api/projects/{project_id}/locations")
        assert loc_res.status_code == 200
        loc_list = loc_res.json()
        assert len(loc_list) == 4
        print(f"   Locations verified: {', '.join(l['name'] for l in loc_list)}")

        # 6. Generate Schedule with Google OR-Tools CP-SAT Discrete Optimization
        print("Running Google OR-Tools CP-SAT discrete optimization solver...")
        gen_res = await client.post(f"/api/projects/{project_id}/schedule/generate", json={
            "objective_profile": "BALANCED"
        })
        assert gen_res.status_code == 200, f"Schedule generation failed: {gen_res.text}"
        sched = gen_res.json()
        version_id = sched["id"]
        print(f"[OK] 6. Schedule Generated (Version {sched['version_number']}): {sched['total_shooting_days']} shooting days, Quality Score: {sched['quality_score']}/100")
        print(f"   AI Review Summary: {sched['explanation'][:120]}...")

        # 7. Verify Astronomical Lighting & Weather in Shooting Days
        assert len(sched["shooting_days"]) > 0
        first_day = sched["shooting_days"][0]
        assert first_day["call_time"] is not None
        assert first_day["wrap_time"] is not None
        print(f"[OK] 7. Day 1 stripboard: Date {first_day['date']} | Call: {first_day['call_time']} -> Wrap: {first_day['wrap_time']} | Sunrise: {first_day['sunrise_time']}, Sunset: {first_day['sunset_time']} | Weather: {first_day['weather_summary']}")

        # 8. Test Scene Lock
        first_item = first_day["items"][0]
        lock_res = await client.post(f"/api/projects/{project_id}/schedule/lock-scene", json={
            "scene_id": first_item["scene_id"],
            "is_locked": True,
            "locked_day_number": 1,
            "locked_start_time": first_item["planned_start_time"]
        })
        assert lock_res.status_code == 200
        print(f"[OK] 8. Scene Lock Tested: Scene {first_item['scene']['scene_code']} locked to Day 1")

        # 9. Test What-If Rescheduling Sandbox
        whatif_res = await client.post(f"/api/projects/{project_id}/schedule/what-if", json={
            "scenario_type": "cast_unavailable",
            "parameters": {
                "cast_member_name": "Meera",
                "date": first_day["date"]
            }
        })
        assert whatif_res.status_code == 200
        wi_data = whatif_res.json()
        print(f"[OK] 9. What-If Simulation: Feasible={wi_data['feasible']} - {wi_data['message']}")

        # 10. Test PDF Call Sheet Export
        pdf_res = await client.get(f"/api/projects/{project_id}/schedule/export/pdf?version_id={version_id}")
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert len(pdf_res.content) > 1000
        assert pdf_res.content.startswith(b"%PDF")
        print(f"[OK] 10. PDF Call Sheet Exported: {len(pdf_res.content)} bytes generated successfully")

    print("\n=== ALL 10 V2 END-TO-END VERIFICATION CHECKS PASSED PERFECTLY ===")

if __name__ == "__main__":
    asyncio.run(run_v2_e2e_verification())
