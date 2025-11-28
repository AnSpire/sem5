from app.services.services import coords_to_linestring, GenerateRouteResponse
from shapely.geometry import mapping, shape, Point
from shapely.ops import unary_union
from app.models.HeatLine import HeatlineSegment, HeatlineBuffer
from app.dto.dto import BufferResponse
from app.repositories.geo import GeoRepository
from sqlalchemy import select
from fastapi import HTTPException

class GeoService():
    def __init__(self, repository: GeoRepository):
        self.repository = repository

    async def generate_route(self, points):
        line = coords_to_linestring(points)
        length = line.length
        geojson_line = mapping(line)
        segment = HeatlineSegment(
            geometry=geojson_line,
            length=length
        )
        self.repository.create_segment(segment=segment)

        return GenerateRouteResponse(
            id=segment.id,
            length=length,
            geometry=geojson_line
        )
    
    async def generate_buffer(self, distance: int):
        segments = await self.repository.get_all_segments()
        if not segments:
            raise HTTPException(400, "Нет сохранённых участков теплотрассы")

        lines = [shape(seg.geometry) for seg in segments]

        merged = unary_union(lines)

        buffer_polygon = merged.buffer(distance)

        geojson_buffer = mapping(buffer_polygon)

        buffer_obj = HeatlineBuffer(
            geometry=geojson_buffer,
            distance=distance
        )
        await self.repository.create_buffer(buffer=buffer_obj)

        return BufferResponse(
            id=buffer_obj.id,
            distance=distance,
            geometry=geojson_buffer
        )