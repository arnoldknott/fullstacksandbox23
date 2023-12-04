# from config import config
# from sqlmodel import Session, SQLmodel, create_engine  # noqa: F401

# postgres = create_engine(config.POSTGRES_URL)


# def get_session():
#     with Session(postgres) as session:
#         yield session


# then, I can handle database crud like this:
# @app.get("/items/")
# def read_items(session: Session = Depends(get_session)):
#     result = session.exec(select(Item)).all()
#     return result
