from typing import List, Any
from pydantic import BaseModel, Field


class Coord(BaseModel):
    """
    Одна точка на плоскости.
    Для простоты считаем, что x и y — это уже условные метры,
    а не долгота/широта.
    """
    x: float = Field(..., description="Координата X")
    y: float = Field(..., description="Координата Y")


class GenerateRouteRequest(BaseModel):
    points: List[Coord] = Field(
        ..., min_items=2,
        description="Список точек, через которые проходит теплотрасса",
    )


class GenerateRouteResponse(BaseModel):
    length: float = Field(..., description="Длина линии (в условных единицах)")
    geometry: dict[str, Any] = Field(
        ..., description="GeoJSON-представление LineString"
    )


class BufferRequest(BaseModel):
    distance: float = Field(..., gt=0)


class BufferResponse(BaseModel):
    id: int
    distance: float
    geometry: dict


class HouseRequest(BaseModel):
    x: float
    y: float



class HouseCheckResponse(BaseModel):
    in_service_zone: bool = Field(..., description="Дом в зоне обслуживания?")
    distance: float = Field(
        ..., description="Фактическое расстояние от дома до линии теплотрассы"
    )
    house_geometry: dict[str, Any] = Field(
        ..., description="GeoJSON точки дома"
    )
    service_zone_geometry: dict[str, Any] = Field(
        ..., description="GeoJSON буфера вокруг линии теплотрассы"
    )

