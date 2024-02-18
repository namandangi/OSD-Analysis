from typing import Optional, Any, List
from sqlmodel import Field, SQLModel, Integer, Float, JSON, Relationship, ARRAY
from datetime import datetime
from sqlalchemy import Column, BigInteger, UniqueConstraint, String, func
from geoalchemy2.types import Geometry
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship


class DSAImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)    
    apiURL: str
    imageId: str = Field(sa_column=Column("imageId", String, unique=True))
    imageName: str
    levels: int
    magnification: Optional[float]
    mm_x: Optional[float]
    mm_y: Optional[float]
    sizeX: int
    sizeY: int
    tileWidth: int
    tileHeight: int
    features: Optional[List["CellFeatures"]] = Relationship(back_populates="image")

from sqlalchemy.dialects import (
    postgresql,
)  # ARRAY contains requires dialect specific type


class CellFeatures(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)    
    # localFeatureId: int
    localFeatureId: str
    Cell_Centroid_X: float
    Cell_Centroid_Y: float
    Point_Vector: List[float] = Field(sa_column=Column(Vector(2)))
    Cell_Area: float
    Percent_Epithelium: float
    Percent_Stroma: float
    Nuc_Area: float
    Mem_Area: float
    Cyt_Area: float
    imageID: Optional[str] = Field(default=None, foreign_key = "dsaimage.imageId")
    image: Optional[DSAImage] = Relationship(back_populates="features")
    Stain_Marker_Embeddings: List[float] = Field(sa_column=Column(Vector()))

    class Config:
        arbitrary_types_allowed = True


class SimpleRectangles(SQLModel, table=True):
    rectangle_id: int = Field(primary_key=True)
    slide_id: str
    x1: int
    x2: int
    y1: int
    y2: int
    shapeName: str
    shapeLabel: str
    shapeLocation: Optional[Any] = Field(sa_column=Column(Geometry("GEOMETRY")))

class SimplePoint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) 
    point: List[float] = Field(sa_column=Column(Vector(2)))
