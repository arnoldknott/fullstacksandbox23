from core.config import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# from sqlmodel import SQLmodel  # noqa: F401

postgres_async_engine = create_async_engine(config.POSTGRES_URL)


async def get_async_session() -> AsyncSession:
    """Returns a database session."""
    async_session = sessionmaker(
        bind=postgres_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session(postgres_async_engine) as session:
        yield session


# postgres = create_engine(config.POSTGRES_URL)

# then, I can handle database crud like this:
# @app.get("/items/")
# def read_items(session: Session = Depends(get_session)):
#     result = session.exec(select(Item)).all()
#     return result
