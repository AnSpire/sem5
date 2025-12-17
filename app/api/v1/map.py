from fastapi import APIRouter, Depends
from app.dependecies.citygen import get_city_generator
from citygen.generate import CityGenerator
from app.serializers.city_layot_to_geojson import city_layout_to_geojson
import json

map_router = APIRouter(tags=["map"])



@map_router.post("/generate")
async def create_map(city_generator: CityGenerator=Depends(get_city_generator)):
    layout = city_layout_to_geojson(city_generator.generate())
    return layout


