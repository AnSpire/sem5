from shapely.geometry import mapping  # для преобразования геометрии в GeoJSON-подобный dict
from app.dto.dto import *
from app.services.services import coords_to_linestring, coord_to_point
from fastapi import APIRouter, Depends
from app.dependecies.db import get_session
from app.models.HeatLine import HeatlineSegment
from sqlalchemy.ext.asyncio import AsyncSession


geo_router = APIRouter(tags=["geo"])

@geo_router.get("/")
def root():
    return {
        "message": "Heatlines Playground API. Перейдите на /docs, чтобы увидеть Swagger UI."
    }


@geo_router.post("/routes/generate", response_model=GenerateRouteResponse)
async def generate_route(
    payload: GenerateRouteRequest,
    session: AsyncSession = Depends(get_session),
):
    line = coords_to_linestring(payload.points)
    length = line.length
    geojson_line = mapping(line)
    segment = HeatlineSegment(
        geometry=geojson_line,
        length=length
    )

    session.add(segment)
    await session.commit()
    await session.refresh(segment)

    return GenerateRouteResponse(
        id=segment.id,
        length=length,
        geometry=geojson_line
    )


@geo_router.post("/routes/buffer", response_model=BufferResponse)
def build_buffer(payload: BufferRequest):
    """
    Построить буфер (зону обслуживания) вокруг линии теплотрассы.
    """
    line = coords_to_linestring(payload.points)
    buffer_poly = line.buffer(payload.distance)

    area = buffer_poly.area
    geojson_polygon = mapping(buffer_poly)  # {"type": "Polygon", ...}

    return BufferResponse(
        distance=payload.distance,
        area=area,
        geometry=geojson_polygon,
    )


@geo_router.post("/routes/check-house", response_model=HouseCheckResponse)
def check_house(payload: HouseCheckRequest):
    """
    Проверить, попадает ли дом в зону обслуживания теплотрассы
    с заданным радиусом max_distance.
    """
    line = coords_to_linestring(payload.line_points)
    house_point = coord_to_point(payload.house)

    distance = line.distance(house_point)
    in_service_zone = distance <= payload.max_distance

    service_zone = line.buffer(payload.max_distance)

    house_geojson = mapping(house_point)
    zone_geojson = mapping(service_zone)

    return HouseCheckResponse(
        in_service_zone=in_service_zone,
        distance=distance,
        house_geometry=house_geojson,
        service_zone_geometry=zone_geojson,
    )