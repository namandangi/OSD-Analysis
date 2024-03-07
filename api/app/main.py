from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, File, UploadFile
from sqlmodel import Session, select
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Distance, ST_AsGeoJSON, ST_MakeEnvelope
from sqlalchemy.orm import load_only
from sqlalchemy import func, and_, delete, desc
import numpy as np
import csv
import codecs
import json
import random, requests
import girder_client
from typing import List, Optional
from .utils import computeColorSimilarityForFeatureSet


from .services import engine, create_db_and_tables
from .models import SimpleRectangles, DSAImage, CellFeatures, SimplePoint
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

@app.post("/add-point")
async def store_points(x: float, y: float):
    pt = [x,y]
    # point = SimplePoint(point=np.array(pt, dtype=np.float32))
    point = SimplePoint(point=pt) # pt gets stored in the table as nd numpy array of type float32
    with Session(engine) as session:
        try:
            print(point)
            session.add(point)
            session.commit()
        except Exception as e:
            print(f"Adding points failed due to {e}")
    return f"Added point {pt}"

@app.get("/get-points")
async def get_points():
    with Session(engine) as session:
        try:
            points = session.query(SimplePoint).all()
            print(type(points[0].__dict__['point']))
            convert_tolist = lambda x : x.tolist(); 
            result = []
            for point in points:
                point_obj = point.__dict__
                del point_obj['_sa_instance_state']
                point_obj['point'] = convert_tolist(point_obj['point']) # type is numpy.ndarray                
                result.append(point_obj)
            return result
        except Exception as e:
            print(f"Retriving points failed due to {e}")

@app.get("/get-similar-pts")
async def get_similar_pts(x: float, y: float, dst: float, lmt: Optional[int] = 10):
    with Session(engine) as session:
        try:
            pt = [x,y]
            points = session.scalars(select(SimplePoint).filter(SimplePoint.point.l2_distance(pt) < dst).limit(lmt)) # returns within dist
            # points = session.scalars(select(SimplePoint).order_by(SimplePoint.point.l2_distance(pt)).limit(5)) # limit no of neighbors
            print(type(points))
            result = []
            for pt in points:
                print(pt)
                nparray = pt.point # type is numpy.ndarray
                if nparray is None: 
                    continue
                print(nparray)
                pt.point = nparray.tolist()
                result.append(pt)
            return result
        except Exception as e:
            print(f"Retriving points failed due to {e}")

# IMAGE ENDPOINTS

@app.get("/lookupImageId")
async def lookupImageById(imageId: str):
    with Session(engine) as session:
        imageInfo = session.query(DSAImage).filter(DSAImage.imageId == imageId).first()
        return imageInfo

    return None

def lookupImageByName(imageName: str):
    with Session(engine) as session:
        image_info = session.query(DSAImage).filter(DSAImage.imageName.startswith(imageName)).first()
        return image_info

@app.get("/lookupImageName")
async def findImageByName(imageName: str):
    imageInfo = lookupImageByName(imageName)
    return imageInfo



@app.get("/get-image-list/")
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
                print(gc.get(f"item/{imageId}"))
                itemInfo = gc.get(f"item/{imageId}")
                print(itemInfo)
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
        image_info = lookupImageByName(image_name)
        imageID = image_info.imageId

        cell_features = []
        cell_embeddings = []
        csv_reader = csv.reader(codecs.iterdecode(file.file,'utf-8'))
        _headers = next(csv_reader, None)
        for row in csv_reader:
            cell_features.append(row[2:11])
            cell_embeddings.append(row[11:])

        transformed_cell_feature_id = []
        with Session(engine) as session:
            for id, row in enumerate(cell_features):
                rid, row_ = row[0], row[1:]
                row_ = [float(val) for val in row_]
                
                pt_vector = [row_[0], row_[1]]
                print((pt_vector))

                transformed_data = CellFeatures(
                    localFeatureId = rid,
                    Cell_Centroid_X = row_[0],
                    Cell_Centroid_Y = row_[1],
                    Point_Vector = [row_[0], row_[1]],
                    Cell_Area = row_[2],
                    Percent_Epithelium = row_[3],
                    Percent_Stroma = row_[4],
                    Nuc_Area = row_[5],
                    Mem_Area = row_[6],
                    Cyt_Area = row_[7],
                    imageID = imageID,
                    Stain_Marker_Embeddings = cell_embeddings[id]
                )
                transformed_cell_feature_id.append(rid)
                session.add(transformed_data)
            session.commit()
            total_records = len(transformed_cell_feature_id)
            return {f"Added {total_records} record to the DB"}
        return {"Msg": "Error Saving"}
    except Exception as e:
        print(f"Failed uploading CSV with error {e}")
    

@app.get("/get-all-features")
async def get_cell_features(lmt: Optional[int] = 5):
    with Session(engine) as session:
        try:
            features = session.query(CellFeatures).limit(lmt).all()
            print(f"found {len(features)} records")
            convert_tolist = lambda x : x.tolist(); 
            for feature in features:
                feature.Point_Vector = convert_tolist(feature.Point_Vector)
                feature.Stain_Marker_Embeddings = convert_tolist(feature.Stain_Marker_Embeddings)
            return features
        except Exception as e:
            print(f"Retriving images failed due to {e}")


@app.get("/get-similar-feat")
async def get_similar_features(x: float, y: float, dst: float, order_list: Optional[str], lmt: Optional[int] = 10):
    with Session(engine) as session:
        try:
            pt = [x,y]
            order_list = order_list.split(",")
            # query = select(CellFeatures).filter(CellFeatures.Point_Vector.l2_distance(pt) < dst).order_by(CellFeatures.Nuc_Area)
            query = select(CellFeatures).filter(CellFeatures.Point_Vector.l2_distance(pt) < dst)
            for order_clause in order_list:
                if order_clause == "Cell_Area":
                    query.order_by(CellFeatures.Cell_Area)
                elif order_clause == "Nuc_Area":
                    query.order_by(CellFeatures.Nuc_Area)
                elif order_clause == "Cyt_Area":
                    query.order_by(CellFeatures.Cyt_Area)
                elif order_clause == "Mem_Area":
                    query.order_by(CellFeatures.Mem_Area)
                elif order_clause == "Percent_Stroma":
                    query.order_by(CellFeatures.Percent_Stroma)
                elif order_clause == "Percent_Epithelium":
                    query.order_by(CellFeatures.Percent_Epithelium)

            points = session.scalars(query.limit(lmt)) # returns within dist                       
            
            # points = session.scalars(select(CellFeatures).filter(CellFeatures.Point_Vector.l2_distance(pt) < dst).limit(lmt)) # returns within dist
            # points = session.scalars(select(CellFeatures).filter(CellFeatures.Point_Vector.l2_distance(pt) < dst).order_by(CellFeatures.Cell_Area).limit(lmt)) # returns within dist
            
            convert_tolist = lambda x : x.tolist(); 
            result = []
            for pt in points:
                if pt.Point_Vector is None: 
                    continue
                pt.Point_Vector = convert_tolist(pt.Point_Vector) # type is numpy.ndarray
                pt.Stain_Marker_Embeddings = convert_tolist(pt.Stain_Marker_Embeddings) # type is numpy.ndarray
                result.append(pt)
            return result
        except Exception as e:
            print(f"Retriving points failed due to {e}")

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





