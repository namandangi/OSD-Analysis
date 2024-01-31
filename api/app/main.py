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
from .models import SimpleRectangles, DSAImage
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
async def lookupImage(imageId: str, dsaApiUrl: str):
    with Session(engine) as session:
        imageInfo = session.query(DSAImage).filter(DSAImage.imageId == imageId).first()
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

            except Exception as e:
                print(f"Error while saving DSA Image: {e}")
        else:
            return exist


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
        try:
            rectangle = session.query(SimpleRectangles).all()
            if rectangle:
                rectSet = [r for r in rectangle]
                print(len(rectSet))
                print(rectSet[0])
                return len(rectSet)
            return []
        except Exception as e:
            print(f"Error getting rectangles: {e}")





