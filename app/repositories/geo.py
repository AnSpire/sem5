


class GeoRepository():
    def __init__(self, session):
        self.session = session

    async def create_segment(self, segment):
        self.session.add(segment)
        await self.session.commit()
        await self.session.refresh(segment)