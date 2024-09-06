from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import config

# from sqlmodel import SQLmodel  # noqa: F401

postgres_async_engine = create_async_engine(
    config.POSTGRES_URL.unicode_string()
)  # TBD: remove echo=True


async def get_async_session() -> AsyncSession:
    """Returns a database session."""
    async_session = async_sessionmaker(
        bind=postgres_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session()


# # This is handled by __aenter__ and __aexit__ in BaseCRUD
# # in case a session is required elsewhere, use this function!
# async def use_async_session() -> AsyncSession:
#     """Yields a database session."""
#     async_session = get_async_session()
#     async with async_session() as session:
#         yield session
#     # session.close()
