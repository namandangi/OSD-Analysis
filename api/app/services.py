from sqlmodel import SQLModel, create_engine
from .models import *

DATABASE_URL = "postgresql://docker:docker@gisdb:5435/osdgis"

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
