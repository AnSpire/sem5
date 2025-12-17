from fastapi import APIRouter, Depends
from app.dependecies.citygen import get_city_generator
from citygen.generate import CityGenerator


map_router = APIRouter(tags=["map"])



@map_router.post("/create")
async def create_map(city_generator: CityGenerator=Depends(get_city_generator)):
    layout = city_generator.generate()
    print(layout)
    return {"hello": "world"}


