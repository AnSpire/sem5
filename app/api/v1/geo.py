from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shapely.geometry import mapping, shape, Point
from shapely.ops import unary_union

from app.dependecies.db import get_session
from app.dependecies.geo import get_geo_service
from app.dto.dto import (
    GenerateRouteRequest,
    GenerateRouteResponse,
    BufferRequest,
    BufferResponse,
    HouseRequest
)
from app.models.HeatLine import HeatlineSegment, HeatlineBuffer
from app.services.services import coords_to_linestring
from app.services.geo import GeoService

geo_router = APIRouter(tags=["geo"])

@geo_router.get("/")
def root():
    return {
        "message": "Heatlines Playground API. Перейдите на /docs, чтобы увидеть Swagger UI."
    }


@geo_router.post("/routes/generate", response_model=GenerateRouteResponse)
async def generate_route(
    payload: GenerateRouteRequest,
    service: GeoService = Depends(get_geo_service)
):
    response = await service.generate_route(payload.points)
    return response

@geo_router.post("/routes/buffer", response_model=BufferResponse)
async def generate_buffer(
    payload: BufferRequest,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(HeatlineSegment))
    segments = result.scalars().all()

    if not segments:
        raise HTTPException(400, "Нет сохранённых участков теплотрассы")

    lines = [shape(seg.geometry) for seg in segments]

    merged = unary_union(lines)

    buffer_polygon = merged.buffer(payload.distance)

    geojson_buffer = mapping(buffer_polygon)

    buffer_obj = HeatlineBuffer(
        geometry=geojson_buffer,
        distance=payload.distance
    )

    session.add(buffer_obj)
    await session.commit()
    await session.refresh(buffer_obj)

    return BufferResponse(
        id=buffer_obj.id,
        distance=payload.distance,
        geometry=geojson_buffer
    )



@geo_router.post("/routes/check-house")
async def check_house(
    payload: HouseRequest,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(HeatlineBuffer).order_by(HeatlineBuffer.id.desc())
    )
    buffer_obj = result.scalars().first()

    if not buffer_obj:
        raise HTTPException(400, "Буфер ещё не создан. Вызовите /routes/buffer")

    buffer_poly = shape(buffer_obj.geometry)
    house_point = Point(payload.x, payload.y)

    in_zone = buffer_poly.contains(house_point)

    distance = buffer_poly.distance(house_point)

    return {
        "in_service_zone": in_zone,
        "distance_to_zone": distance,
        "buffer_id": buffer_obj.id
    }
