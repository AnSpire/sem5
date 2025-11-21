from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:1111@localhost:5432/geo-postgres"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,       
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
