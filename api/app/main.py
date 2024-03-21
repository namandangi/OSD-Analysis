from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, File, UploadFile
from sqlmodel import Session, select
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Distance, ST_AsGeoJSON, ST_MakeEnvelope
from sqlalchemy.orm import load_only
from sqlalchemy import func, and_, delete, desc
import numpy as np
import pandas as pd
import csv
import codecs
import json
import random, requests
import girder_client
from typing import List, Optional
from .utils import computeColorSimilarityForFeatureSet


from .services import engine, create_db_and_tables
from .models import DSAImage, CellFeatures
# from .models import SimpleRectangles, SimplePoint
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

# FEATURE ENDPOINTS
 
@app.get("/get-all-features")
async def get_cell_features(lmt: Optional[int] = 5):
    with Session(engine) as session:
        try:
            features = session.query(CellFeatures).limit(lmt).all()
            print(f"found {len(features)} records")
            convert_tolist = lambda x : x.tolist(); 
            for feature in features:
                if feature.Point_Vector: 
                    feature.Point_Vector = convert_tolist(feature.Point_Vector)
                if feature.Stain_Marker_Embeddings:
                    feature.Stain_Marker_Embeddings = convert_tolist(feature.Stain_Marker_Embeddings)
            return features
        except Exception as e:
            print(f"Retriving images failed due to {e}")

@app.get("/get-feature/")
async def get_cell_feature_by_id(UniqueID: str):
    with Session(engine) as session:
        print("UniqueID", UniqueID)
        try:
            feature = session.query(CellFeatures).filter(CellFeatures.localFeatureId == UniqueID).first() # UniqueID
            
            convert_tolist = lambda x : x.tolist()

            feature.Point_Vector = convert_tolist(feature.Point_Vector)
            if feature.Stain_Marker_Embeddings:
                feature.Stain_Marker_Embeddings = convert_tolist(feature.Stain_Marker_Embeddings)
            return feature            
        except Exception as e:
            print(f"Retriving images failed due to {e}")

@app.get("/get-similar-feat")
async def get_similar_features(x: float, y: float, dst: float, imageID: str, order_list: Optional[str], lmt: Optional[int] = 10):
    with Session(engine) as session:
        try:
            pt = [x,y]
            order_list = order_list.split(",")
            # query = select(CellFeatures).filter(CellFeatures.Point_Vector.l2_distance(pt) < dst).order_by(CellFeatures.Nuc_Area)
            # query = select(CellFeatures).filter(CellFeatures.Point_Vector.l2_distance(pt) < dst)
            # query = select(CellFeatures).filter(CellFeatures.imageID == imageID).filter(CellFeatures.Point_Vector.l2_distance(pt) < dst)
            query = select(CellFeatures).filter(CellFeatures.imageID == imageID).filter(CellFeatures.Point_Vector.l2_distance(pt) < dst)
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
            for ptx in points:
                if ptx.Point_Vector is None: 
                    continue
                ptx.Point_Vector = convert_tolist(ptx.Point_Vector) # type is numpy.ndarray
                ptx.Stain_Marker_Embeddings = convert_tolist(ptx.Stain_Marker_Embeddings) # type is numpy.ndarray
                result.append(ptx)
            return result
        except Exception as e:
            print(f"Retriving points failed due to {e}")

@app.post("/upload-cell-features/")
async def upload_feature_csv(imageID: str, file: UploadFile = File(...)):
    try:
                
        df = pd.read_csv(file.file)
        df.dropna(inplace=True)

        feature_id = df.iloc[:, 2].values
        cell_features = df.iloc[:, 3:11].values.astype(float)
        cell_embeddings = df.iloc[:, 11:].values.astype(float)

        transformed_cell_feature_id = []

        with Session(engine) as session:
            for id, row in enumerate(cell_features):
                
                rid = feature_id[id]

                transformed_data = CellFeatures(
                    localFeatureId = rid,
                    Cell_Centroid_X = row[0],
                    Cell_Centroid_Y = row[1],
                    Point_Vector = [row[0], row[1]],
                    Cell_Area = row[2],
                    Percent_Epithelium = row[3],
                    Percent_Stroma = row[4],
                    Nuc_Area = row[5],
                    Mem_Area = row[6],
                    Cyt_Area = row[7],
                    Stain_Marker_Embeddings = cell_embeddings[id].tolist(),
                    imageID = imageID,
                )
                transformed_cell_feature_id.append(rid)
                session.add(transformed_data)
            session.commit()
            total_records = len(transformed_cell_feature_id)
            return {f"Added {total_records} record to the DB"}
        return {"Msg": "Error Saving"}
    except Exception as e:
        print(f"Failed uploading CSV with error {e}")