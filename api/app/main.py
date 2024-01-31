from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Distance, ST_AsGeoJSON, ST_MakeEnvelope
from sqlalchemy.orm import load_only
from sqlalchemy import func, and_, delete
import numpy as np
import random, requests
import girder_client
from typing import List
from .utils import computeColorSimilarityForFeatureSet


from .services import engine, create_db_and_tables
from .models import SimpleRectangles, DSAImage, tileFeatures, featureExtractionParams, imageFeatureSets, NPfeatureSet
from .utils import extend_dict, pretify_address

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Msg": "Hello World"}

# IMAGE ENDPOINTS

@app.get("/lookupImage")
async def lookupImage(imageName: str, dsaApiUrl: str):
    with Session(engine) as session:
        imageInfo = session.query(DSAImage).filter(DSAImage.imageName == imageName).first()
        return imageInfo

    return None

@app.get("/getImageList/")
async def get_imageList():
    with Session(engine) as session:
        images = session.query(DSAImage).all()
        print(len(images))
        return images

@app.post("/add-DSAImage/")
async def add_DSAImage(imageId: str, dsaApiUrl: str):
    with Session(engine) as session:
        exist = session.query(DSAImage).filter(DSAImage.imageId == imageId).first()

        if not exist:
            gc = girder_client.GirderClient(apiUrl=dsaApiUrl)

            try:
                resp = requests.get(dsaApiUrl, timeout=1)
                itemInfo = gc.get(f"item/{imageId}")
                tileData = gc.get(f"item/{imageId}/tiles")

                imageItem = DSAImage(
                    imageName=itemInfo["name"],
                    apiURL=dsaApiUrl,
                    imageId=imageId,
                    magnification=tileData["magnification"],
                    mm_x=tileData["mm_x"],
                    mm_y=tileData["mm_y"],
                    sizeX=tileData["sizeX"],
                    sizeY=tileData["sizeY"],
                    levels=tileData["levels"],
                    tileWidth=tileData["tileWidth"],
                    tileHeight=tileData["tileHeight"],
                )

                session.add(imageItem)
                session.commit()
                session.refresh(imageItem)
                return imageItem

            except:
                print("Having an issue with one of the DSA servers")
        else:
            return exist


#  TILE END POINTS

@app.post("/addTileFeatures")
async def post_tileFeatures(featureBatch: List[tileFeatures]):
    tileData = [tile_obj.dict() for tile_obj in featureBatch]
    with Session(engine) as session:
        session.bulk_insert_mappings(tileFeatures, tileData)
        session.commit()
    return "Tile Feature Data added"

## TO DO: Add optinoal parameter that will return all fields, not just the ones listed below
@app.get("/getTileFeatures")
async def get_tileFeatures(ftxtract_id: int):

    with Session(engine) as session:
        tileData = (
            session.query(tileFeatures)
            .filter(tileFeatures.ftxtract_id == ftxtract_id)
            .options(
                load_only(
                    tileFeatures.imageId,
                    tileFeatures.topX,
                    tileFeatures.topY,
                    tileFeatures.width,
                    tileFeatures.height,
                    tileFeatures.average,
                    tileFeatures.localTileId,
                )
            )
            .limit(10000)
            .all()
        )
        return tileData

    return None

@app.delete("/deleteTileFeatures")
async def delete_tileFeatures(imageId: str, ftxtract_id: int):
    """This will delete tiles associated with an image in case I want to regenerate them"""
    with Session(engine) as session:
        statement = (
            delete(tileFeatures).where(tileFeatures.imageId == imageId).where(tileFeatures.ftxtract_id == ftxtract_id)
        )
        result = session.exec(statement)
        session.commit()
        return "Tile Feature Data Truncated  "  # % result.rowCount

# FEATURES

@app.get("/getNPfeatures")
async def get_NPfeatures(imageFeatureSet_id: int):

    with Session(engine) as session:
        NPfeatureData = (
            session.query(NPfeatureSet)
            .filter(NPfeatureSet.imageFeatureSet_id == imageFeatureSet_id)
            # .filter(tileFeatures.imageId == imageId)
            # .options(
            #     load_only(
            #         tileFeatures.imageId,
            #         tileFeatures.topX,
            #         tileFeatures.topY,
            #         tileFeatures.width,
            #         tileFeatures.height,
            #         tileFeatures.average,
            #         tileFeatures.localTileId,
            #     )
            # )
            .limit(10000)
            .all()
        )
        return NPfeatureData

    return None

@app.get("/getFeatureSets")
async def get_featureSets(imageId: str):  # , featureType: str, imageFeatureSet_id: int):
    with Session(engine) as session:
        featureSets = session.query(imageFeatureSets).filter(imageFeatureSets.imageId == imageId).all()

        return featureSets
    return None


@app.get("/computeFeatureDistance")
async def get_computeFeatureDistance(ftxtract_id: int, distanceThresh: float, refFeatureId: str):
    ### Given a ftxtract_id and a reference vector, and a distance
    ### Compute which tiles (or features) are within the defined metric
    with Session(engine) as session:
        featureSelectedData = (
            session.query(tileFeatures)
            .filter(tileFeatures.ftxtract_id == ftxtract_id)
            .options(load_only(tileFeatures.imageId, tileFeatures.localTileId, tileFeatures.average))
            .all()
        )

        refFeatureVector = (
            session.query(tileFeatures)
            .filter(tileFeatures.ftxtract_id == ftxtract_id)
            .filter(tileFeatures.localTileId == refFeatureId)
            .options(load_only(tileFeatures.average))
            .first()
        )
        ftrDistances = computeColorSimilarityForFeatureSet(
            featureSelectedData, refFeatureVector.average, distanceThresh
        )
        return ftrDistances
    return None


@app.post("/addFeatureExtractionParams")
async def insert_featureExtractionParams(featXtractParams: featureExtractionParams):
    print("Adding parameters used to do a certain tile feature extraction")
    with Session(engine) as session:
        exist = (
            session.query(featureExtractionParams)
            .filter(featureExtractionParams.imageId == featXtractParams.imageId)
            .filter(featureExtractionParams.tileWidth == featXtractParams.tileWidth)
            .filter(featureExtractionParams.magnification == featXtractParams.magnification)
            .first()
        )
        if exist:
            return exist
        else:
            ftr = session.add(featXtractParams)
            session.commit()
            session.refresh(featXtractParams)
            return featXtractParams  ## This should return a fresh copy of the extracted feature..

    return None


@app.post("/lookupFeatureExtractionParams")
async def lookup_featureExtractionParams(imageId: str, magnification: float, tileSizeParam: str):
    print("This will determine if a set of feature extractions have already been run at this resolution")
    with Session(engine) as session:
        exist = (
            session.query(featureExtractionParams)
            .filter(featureExtractionParams.imageId == imageId)
            .filter(featureExtractionParams.tileSizeParam == tileSizeParam)
            .filter(featureExtractionParams.magnification == magnification)
            .first()
        )
        if exist:
            return exist
        else:
            return None
    return None


@app.post("/getFeatureSetId")
async def get_featureSetId(imageId: str, magnification: float, tileSizeParam: str):
    print("This will determine if a set of feature extractions have already been run at this resolution")
    with Session(engine) as session:
        exist = (
            session.query(featureExtractionParams)
            .filter(featureExtractionParams.imageId == imageId)
            .filter(featureExtractionParams.tileSizeParam == tileSizeParam)
            .filter(featureExtractionParams.magnification == magnification)
            .first()
        )
        if exist:
            return exist
        else:
            return None
    return None



    return None

# RECTANGLES

@app.get("/insert_random_rects/")
async def gen_random_rects(slide_id: str):
    ### Let's generate 500 random shapes...
    numShapesToGen = 5
    max_X = 10000
    max_Y = 10000
    boxSize_X = 40
    boxSixe_Y = 50

    with Session(engine) as session:
        for i in range(numShapesToGen):
            x1 = random.randrange(0, max_X)
            y1 = random.randrange(0, max_Y)

            x2 = x1 + boxSize_X
            y2 = y1 + boxSixe_Y

            myRect = SimpleRectangles(
                slide_id=slide_id,
                x1=x1,
                x2=x2,
                y1=y1,
                y2=y2,
                shapeName="box",
                shapeLabel="NFT",
                shapeLocation=ST_MakeEnvelope(x1, y1, x2, y2, 4326),
            )
            session.add(myRect)
        session.commit()
    return "Mission Accomplished"


@app.get("/rectangles/")
async def get_rectangles():
    with Session(engine) as session:
        rectangle = session.query(SimpleRectangles).all()
        rectSet = [r for r in rectangle]
        print(len(rectSet))
        print(rectSet[0])
        return len(rectSet)





