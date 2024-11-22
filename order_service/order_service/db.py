from sqlmodel import create_engine, Session
from .settings import DATABASEURL

engine = create_engine(DATABASEURL, echo=True)
def create_table():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session
