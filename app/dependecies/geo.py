from fastapi import Depends
from app.dependecies.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.geo import GeoRepository
from app.services.geo import GeoService

def get_geo_repository(session: AsyncSession = Depends(get_session)):
    return GeoRepository(session=session)

def get_geo_service(repository: GeoRepository = Depends(get_geo_repository)):
    return GeoService(repository=repository)