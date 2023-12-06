from config import config
from sqlmodel import Session, SQLmodel, create_engine  # noqa: F401

# from sqlalchemy import create_engine


engine = create_engine(config.POSTGRES_URL)


async def get_session() -> Session:
    """Returns a database session."""
    async with Session(engine) as session:
        yield session


# postgres = create_engine(config.POSTGRES_URL)

# SQLModel:
# def get_session():
#     with Session(postgres) as session:
#         yield session

# then, I can handle database crud like this:
# @app.get("/items/")
# def read_items(session: Session = Depends(get_session)):
#     result = session.exec(select(Item)).all()
#     return result
