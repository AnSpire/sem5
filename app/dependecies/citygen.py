from fastapi import Depends

from citygen.config import CityConfig
from citygen.generate import CityGenerator
from citygen.houses import HouseGenerator
from citygen.roads import RoadBuilder
from citygen.park import ParkGenerator


def get_config():
    return CityConfig()


def get_city_generator(config=Depends(get_config)):
    return CityGenerator(config)


def get_houses_generator(config=Depends(get_config)):
    return HouseGenerator(config) 