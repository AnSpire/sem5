from fastapi import FastAPI
from shapely.geometry import mapping  # для преобразования геометрии в GeoJSON-подобный dict
from app.dto.dto import *
from app.services.services import coords_to_linestring, coord_to_point

app = FastAPI(
    title="Heatlines Playground API",
    description="Простое демо FastAPI + Shapely для работы с теплотрассами и домами",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Heatlines Playground API. Перейдите на /docs, чтобы увидеть Swagger UI."
    }


@app.post("/routes/generate", response_model=GenerateRouteResponse)
def generate_route(payload: GenerateRouteRequest):
    """
    Построить линию теплотрассы по набору точек и вернуть её длину.
    """
    line = coords_to_linestring(payload.points) 
    length = line.length

    geojson_line = mapping(line)  # {"type": "LineString", "coordinates": [...]}

    return GenerateRouteResponse(
        length=length,
        geometry=geojson_line,
    )


@app.post("/routes/buffer", response_model=BufferResponse)
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


@app.post("/routes/check-house", response_model=HouseCheckResponse)
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
