from fastapi import FastAPI
from shapely.geometry import mapping  # для преобразования геометрии в GeoJSON-подобный dict
from app.dto.dto import *
from app.services.services import coords_to_linestring, coord_to_point
from app.api.v1.geo import geo_router
from app.api.v1.map import map_router

app: FastAPI = FastAPI(
    title="Heatlines Playground API",
    description="Простое демо FastAPI + Shapely для работы с теплотрассами и домами",
    version="0.1.0",
)
app.include_router(geo_router, prefix="/geo")
app.include_router(map_router, prefix="/map")

