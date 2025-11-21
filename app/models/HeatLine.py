from app.models.Base import Base
from sqlalchemy import Column, Integer, Float, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB


class HeatlineSegment(Base):
    __tablename__ = "heatline_segments"

    id = Column(Integer, primary_key=True)
    geometry = Column(JSONB, nullable=False)
    length = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())



class HeatlineBuffer(Base):
    __tablename__ = "heatline_buffers"

    id = Column(Integer, primary_key=True)
    distance = Column(Float, nullable=False)  
    geometry = Column(JSONB, nullable=False)  
    created_at = Column(DateTime, server_default=func.now())
