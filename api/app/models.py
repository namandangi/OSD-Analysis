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

from sqlalchemy.dialects import (
    postgresql,
)  # ARRAY contains requires dialect specific type


class CellFeatures(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)    
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
    Stain_Marker_Embeddings: List[float] = Field(sa_column=Column(Vector()))
    imageID: str = Field(default=None, foreign_key = "dsaimage.imageId")

    class Config:
        arbitrary_types_allowed = True
