import redis
from core.config import config
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

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


# TBD: remove this?
async def use_async_session() -> AsyncSession:
    """Yields a database session."""
    async_session = get_async_session()
    async with async_session() as session:
        yield session


redis_jwks = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD,
    db=config.REDIS_JWKS_DB,
)
