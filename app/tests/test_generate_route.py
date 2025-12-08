import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.dependecies.db import get_session
from app.models.Base import Base
from sqlalchemy import select
from app.models.HeatLine import HeatlineSegment, HeatlineBuffer

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


@pytest.mark.asyncio
async def test_generate_buffer(test_session: AsyncSession):
    segment = HeatlineSegment(
        geometry={"type": "LineString", "coordinates": [[0, 0], [10, 0]]},
        length=10.0
    )
    test_session.add(segment)
    await test_session.commit()
    await test_session.refresh(segment)

    payload = {
        "distance": 5.0
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/geo/routes/buffer", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert data["distance"] == 5.0
    assert data["geometry"]["type"] == "Polygon"

    result = await test_session.execute(
        select(HeatlineBuffer).where(HeatlineBuffer.id == data["id"])
    )
    buffer_obj = result.scalar_one_or_none()

    assert buffer_obj is not None
    assert buffer_obj.distance == 5.0
    assert buffer_obj.geometry["type"] == "Polygon"



@pytest.mark.asyncio
async def test_check_house(test_session):
    segment = HeatlineSegment(
        geometry={"type": "LineString", "coordinates": [[0, 0], [10, 0]]},
        length=10.0
    )
    test_session.add(segment)
    await test_session.commit()
    await test_session.refresh(segment)

    buffer_payload = {"distance": 5.0}

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        buffer_response = await ac.post("/routes/buffer", json=buffer_payload)

    assert buffer_response.status_code == 200
    buffer_data = buffer_response.json()
    buffer_id = buffer_data["id"]

    house_payload = {"x": 5, "y": 1}

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        resp = await ac.post("/routes/check-house", json=house_payload)

    assert resp.status_code == 200

    data = resp.json()

    assert "in_service_zone" in data
    assert "distance_to_zone" in data
    assert "buffer_id" in data

    assert data["buffer_id"] == buffer_id
    assert data["in_service_zone"] is True
    assert data["distance_to_zone"] == 0.0
