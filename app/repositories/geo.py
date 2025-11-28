from sqlalchemy import select
from fastapi import HTTPException
from app.models.HeatLine import HeatlineSegment, HeatlineBuffer


class GeoRepository():
    def __init__(self, session):
        self.session = session

    async def create_segment(self, segment):
        self.session.add(segment)
        await self.session.commit()
        await self.session.refresh(segment)

    async def get_all_segments(self):
        result = await self.session.execute(select(HeatlineSegment))
        segments = result.scalars().all()

        if not segments:
            raise HTTPException(400, "Нет сохранённых участков теплотрассы")

        return segments

    async def create_buffer(self, buffer: HeatlineBuffer):
        self.session.add(buffer)
        await self.session.commit()
        await self.session.refresh(buffer)
        
