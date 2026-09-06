import os
import pytest
import pytest_asyncio
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from app.config import settings
from app.core.database import init_db, engine, Base
from app.main import app

TEST_DB_FILE = "./test_production_plan.db"

@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_test_database():
    settings.DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"
    await init_db()
    yield
    await engine.dispose()
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

@pytest_asyncio.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
