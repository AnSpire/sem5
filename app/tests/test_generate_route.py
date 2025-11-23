import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.dependecies.db import get_session
from app.models.Base import Base


TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5544/testdb"


@pytest.fixture()
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture()
async def test_session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
def override_get_db(test_session):
    app.dependency_overrides[get_session] = lambda: test_session


@pytest.mark.asyncio
async def test_generate_route(test_session):
    payload = {
        "points": [
            {"x": 0, "y": 0},
            {"x": 10, "y": 0}
        ]
    }


    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/geo/routes/generate", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["length"] == 10
    assert data["geometry"]["type"] == "LineString"
