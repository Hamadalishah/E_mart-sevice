from typing import Optional
from sqlmodel import SQLModel,create_engine, Session
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

connection_string:Optional[str] = os.getenv('DATABASEURL')
if not connection_string:
    raise ValueError("DATABASE_URL environment variable not set")


engine = create_engine(connection_string)


    
  
def create_table():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session

    