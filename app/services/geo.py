from app.services.services import coords_to_linestring, GenerateRouteResponse
from shapely.geometry import mapping, shape, Point
from app.models.HeatLine import HeatlineSegment
from app.repositories.geo import GeoRepository

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