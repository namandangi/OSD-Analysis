from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, File, UploadFile
from sqlmodel import Session, select
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Distance, ST_AsGeoJSON, ST_MakeEnvelope
from sqlalchemy.orm import load_only
from sqlalchemy import func, and_, delete
import numpy as np
import csv
import codecs
import random, requests
import girder_client
from typing import List
from .utils import computeColorSimilarityForFeatureSet


from .services import engine, create_db_and_tables
from .models import SimpleRectangles, DSAImage, CellFeatures
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

@app.get("/lookupImageId")
async def lookupImageById(imageId: str):
    with Session(engine) as session:
        imageInfo = session.query(DSAImage).filter(DSAImage.imageId == imageId).first()
        return imageInfo

    return None

def lookupImageByName(imageName: str):
    with Session(engine) as session:
        imageInfo = session.query(DSAImage).filter(DSAImage.imageName == imageId).first()
        return imageInfo

@app.get("/lookupImageName")
async def findImageByName(imageName: str):
    imageInfo = lookupImageByName(imageName)
    return imageInfo



@app.get("/getImageList/")
async def get_imageList():
    with Session(engine) as session:
        try:
            images = session.query(DSAImage).all()
            print(len(images))
            return images
        except Exception as e:
            print(f"Retriving images failed due to {e}")

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


@app.post("/upload-cell-features/")
async def upload_feature_csv(file: UploadFile = File(...)):
    try:
        image_name, _ = file.filename.rsplit('_', 1)
        image_id = lookupImageByName(image_name)
        print(image_id)
        cell_features = []
        keys = ['localFeatureId', 'Cell_Centroid_X', 'Cell_Centroid_Y', 'Cell_Area', 'Percent_Epithelium', 'Percent_Stroma', 'Nuc_Area', 'Mem_Area', 'Cyt_Area']
        csv_reader = csv.reader(codecs.iterdecode(file.file,'utf-8'))
        _headers = next(csv_reader, None)
        for row in csv_reader:
            cell_features.append(row[2:11])
        print(cell_features[0])
        cell_features = [CellFeatures(dict(zip(keys, data))) for data in cell_features]

        with Session(engine) as session:
            session.bulk_add(cell_features)
            session.commit()
            return cell_features
        return
    except Exception as e:
        print(f"Failed uploading CSV with error {e}")
    


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





