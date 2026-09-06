import pytest
from pathlib import Path

@pytest.mark.asyncio
async def test_project_crud_and_upload(client):
    # 1. Create project
    create_res = await client.post("/api/projects", json={
        "name": "Neon Harbor Production",
        "production_type": "Feature Film",
        "director": "Jane Doe",
        "production_company": "Apex Pictures"
    })
    assert create_res.status_code == 201
    proj_data = create_res.json()
    proj_id = proj_data["id"]
    assert proj_data["name"] == "Neon Harbor Production"

    # 2. Upload screenplay
    sample_path = Path("backend/sample_screenplays/neon_harbor.txt")
    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    upload_res = await client.post(
        f"/api/projects/{proj_id}/screenplay",
        files={"file": ("neon_harbor.txt", file_bytes, "text/plain")}
    )
    assert upload_res.status_code == 200
    up_data = upload_res.json()
    assert up_data["scenes_detected"] == 6

    # 3. List scenes
    scenes_res = await client.get(f"/api/projects/{proj_id}/scenes")
    assert scenes_res.status_code == 200
    scenes = scenes_res.json()
    assert len(scenes) == 6

    # 4. Trigger analysis
    analyze_res = await client.post(f"/api/projects/{proj_id}/analyze")
    assert analyze_res.status_code == 200
    job_data = analyze_res.json()
    assert job_data["status"] in ["PENDING", "ANALYZING", "COMPLETED"]

    # 5. Get detail of Scene 1
    scene1_id = scenes[0]["id"]
    s1_res = await client.get(f"/api/projects/{proj_id}/scenes/{scene1_id}")
    assert s1_res.status_code == 200
    s1_data = s1_res.json()
    assert "DOCKS" in s1_data["scene_heading"]

    # 6. Update scene (human edit)
    update_res = await client.put(f"/api/projects/{proj_id}/scenes/{scene1_id}", json={
        "location_name": "Pier 42 Industrial Docks",
        "estimated_duration_minutes": 120,
        "production_notes": "Director requested high-pressure water cannons for background."
    })
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["location_name"] == "Pier 42 Industrial Docks"
    assert updated_data["status"] == "HUMAN_EDITED"

    # 7. Add entity manually
    add_prop_res = await client.post(
        f"/api/projects/{proj_id}/scenes/{scene1_id}/entities",
        json={"entity_type": "prop", "data": {"name": "Flare Gun", "quantity": 1}}
    )
    assert add_prop_res.status_code == 200

    # 8. Confirm scene
    confirm_res = await client.post(f"/api/projects/{proj_id}/scenes/{scene1_id}/confirm")
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "HUMAN_CONFIRMED"

    # 9. Test Exports
    json_export = await client.get(f"/api/projects/{proj_id}/export/json")
    assert json_export.status_code == 200
    assert len(json_export.json()["scenes"]) == 6

    csv_export = await client.get(f"/api/projects/{proj_id}/export/csv")
    assert csv_export.status_code == 200
    assert "Scene Number,Scene Code,Scene Heading" in csv_export.text
