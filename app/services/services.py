from shapely.geometry import Point, LineString
from typing import List, Any
from app.dto.dto import *


def coords_to_linestring(points: List[Coord]) -> LineString:
    """Преобразует список Coord в Shapely LineString."""
    return LineString([(p.x, p.y) for p in points])


def coord_to_point(c: Coord) -> Point:
    """Преобразует Coord в Shapely Point."""
    return Point(c.x, c.y)