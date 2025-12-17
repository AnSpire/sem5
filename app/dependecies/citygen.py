from fastapi import Depends

from citygen.config import CityConfig
from citygen.generate import CityGenerator



def get_config():
    return CityConfig()


def get_city_generator(config=Depends(get_config)):
    return CityGenerator(config)