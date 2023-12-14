from core.config import config
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

# from sqlmodel import SQLmodel  # noqa: F401

postgres_async_engine = create_async_engine(config.POSTGRES_URL.unicode_string())


async def get_async_session() -> AsyncSession:
    """Returns a database session."""
    async_session = async_sessionmaker(
        bind=postgres_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


# postgres = create_engine(config.POSTGRES_URL)

# then, I can handle database crud like this:
# @app.get("/items/")
# def read_items(session: Session = Depends(get_session)):
#     result = session.exec(select(Item)).all()
#     return result
