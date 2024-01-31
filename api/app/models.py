from typing import Optional
from sqlmodel import Field, SQLModel, Integer, Float, JSON
from datetime import datetime
from sqlalchemy import Column, BigInteger
from geoalchemy2.types import Geometry
from typing import Any, List, Optional
from pgvector.sqlalchemy import Vector
from sqlalchemy import UniqueConstraint, Column, String


class DSAImage(SQLModel, table=True, extend_existing=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    apiURL: str
    imageId: str = Field(sa_column=Column("imageId", String, unique=True))
    imageName: str
    levels: int
    magnification: float
    mm_x: float
    mm_y: float
    sizeX: int
    sizeY: int
    tileWidth: int
    tileHeight: int


from sqlalchemy.dialects import (
    postgresql,
)  # ARRAY contains requires dialect specific type

##ID,First ID,UniqueID,Cell_Centroid_X,Cell_Centroid_Y,Cell_Area,Percent_Epithelium,Percent_Stroma,Nuc_Area,Mem_Area,Cyt_Area
# ,ACTININ,BCATENIN,CD11B,CD20,CD3D,CD4,CD45,CD45B,CD68,CD8,CGA,COLLAGEN,COX2,DAPI,ERBB2,FOXP3,GACTIN,HLAA,LYSOZYME,MUC2,NAKATPASE,OLFM4,PANCK,PCNA,PDL1,PEGFR,PSTAT3,SMA,SNA,SOX9,VIMENTIN

"""I am setting the maximum embedding vector size to 50 for now
The Stain_Marker_Embeddings are stored in the feature extraction parameters"""


class VandyCellFeatures(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    localFeatureId: int
    Cell_Centroid_X: float
    Cell_Centroid_Y: float
    Cell_Area: float
    Percent_Epithelium: float
    Percent_Stroma: float
    Nuc_Area: float
    Mem_Area: float
    Cyt_Area: float
    Stain_Marker_Embeddings: List[float] = Field(sa_column=Column(Vector(50)))


class tileFeatures(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    apiURL: str
    imageId: str = Field(index=True)
    imageName: str
    topX: int
    topY: int
    width: int
    height: int
    featureType: str  ### Should be something like imgHistogram
    ftxtract_id: int
    localTileId: str  ## This is most likely the tilePosition in the current run
    red: Optional[List[int]] = Field(default=None, sa_column=Column(postgresql.ARRAY(Integer())))
    green: Optional[List[int]] = Field(default=None, sa_column=Column(postgresql.ARRAY(Integer())))
    blue: Optional[List[int]] = Field(default=None, sa_column=Column(postgresql.ARRAY(Integer())))
    average: Optional[List[float]] = Field(default=None, sa_column=Column(postgresql.ARRAY(Float())))

    # Needed for Column(JSON)
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


class MoreSimpleRectangles(SQLModel, table=True):
    rectangle_id: int = Field(primary_key=True)
    slide_id: str
    x1: int
    x2: int
    y1: int
    y2: int
    shapeName: str
    shapeLabel: str
    shapeLocation: Optional[Any] = Field(sa_column=Column(Geometry("GEOMETRY")))


class featureSetExtractionParams(SQLModel, table=True, extend_existing=True):
    featureSet_id: int = Field(primary_key=True, default=None)
    featureType: str
    featureSetComputeTime: float
    bytesRead: Optional[int] = Field(sa_column=Column(BigInteger()), default=None)
    imageId: str
    totalObjects: int
    magnification: Optional[float]
    extractionParams: dict = Field(sa_column=Column(JSON), default={})
    resultsFileMD5 = str


class featureExtractionParams(SQLModel, table=True, extend_existing=True):
    ftxtract_id: int = Field(primary_key=True, default=None)
    tileWidth: int
    tileHeight: int
    featureType: str
    ftxComputeTime: float
    bytesRead: Optional[int] = Field(sa_column=Column(BigInteger()), default=None)
    imageId: str
    tilesProcessed: int
    sizeX: int
    sizeY: int
    magnification: float


class imageFeatureSets(SQLModel, table=True, extend_existing=True):
    imageFeatureSet_id: int = Field(primary_key=True, default=None)
    featureType: str
    featureComputeTime: Optional[float]
    bytesRead: Optional[int] = Field(sa_column=Column(BigInteger()), default=None)
    imageId: str
    totalObjects: int
    magnification: Optional[float]
    imageFeatureParams: dict = Field(sa_column=Column(JSON), default={})


class NPfeatureSet(SQLModel, table=True, extend_existing=True):
    id: int = Field(primary_key=True, default=None)
    classLabel: str
    topX: int
    topY: int
    roiWidth: int
    roiHeight: int
    featureEmbeddings: str
    imageId: str
    imageFeatureSet_id: int


#     embeddingMap: str  ## If I store an embedding vector for an image, this is the featureList/names for each element
#     tileSizeParam: Optional[str] = Field(default=None)
## This helps me keep track of if I used a native tile sizing or multiple threreof

# {'imageName': 'TCGA-19-1787-01C-01-TS1.b9f6f0f2-14f2-4bc5-b7f8-9520ec38eb98.svs',


# 'imagePath': 'SmallSampleFiles/TCGA-19-1787-01C-01-TS1.b9f6f0f2-14f2-4bc5-b7f8-9520ec38eb98.svs',
# 'opType': 'tileHist', 'startTime': 1683232143.5455363,
# 'elapsedTime': 0.13014698028564453, 'tilesProcessed': 4,
# 'tileWidth': 256, 'tileHeight': 256, 'sizeX': 6000,
#  'sizeY': 7977, 'bytesRead': 747000, 'magnification': 1.25,
# 'tileSizeParam': 'native'}

#     tags: Optional[Set[str]] = Field(default=None, sa_column=Column(postgresql.ARRAY(String())))

# (...)
#         tagged = session.query(Item).filter(Item.tags.contains([tag]))

# from sqlmodel import Field, Session, SQLModel, create_engine, JSON, Column


# class Block(SQLModel, table=True):
#     id: int = Field(..., primary_key=True)
#     values: List[str] = Field(sa_column=Column(JSON))

#     # Needed for Column(JSON)
#     class Config:
#         arbitrary_types_allowed = True


