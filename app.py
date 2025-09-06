
import sys
import os
import certifi
ca = certifi.where()
from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)
import pymongo
from abaloneage.exception.exception import PipelineException
from abaloneage.logging.logger import logging
from abaloneage.pipeline.training_pipeline import TrainingPipeline
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd
from abaloneage.utils.main_utils.utils import load_object
from abaloneage.utils.ml_utils.model.estimator import NetworkModel
client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
from abaloneage.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from abaloneage.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]
app = FastAPI()
from pydantic import BaseModel
# Pydantic model for single prediction
class AbaloneInput(BaseModel):
    sex: str
    length: float
    diameter: float
    height: float
    whole_weight: float
    shucked_weight: float
    viscera_weight: float
    shell_weight: float

@app.post("/predict_single")
async def predict_single(data: AbaloneInput):
    try:
        preprocessor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        X = [[
            data.sex,
            data.length,
            data.diameter,
            data.height,
            data.whole_weight,
            data.shucked_weight,
            data.viscera_weight,
            data.shell_weight
        ]]
        X_transformed = preprocessor.transform(X)
        prediction = final_model.predict(X_transformed)
        return {"predicted_rings": float(prediction[0])}
    except Exception as e:
        raise PipelineException(e, sys)
import sys
import os

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)
import pymongo
from abaloneage.exception.exception import PipelineException
from abaloneage.logging.logger import logging
from abaloneage.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

from abaloneage.utils.main_utils.utils import load_object

from abaloneage.utils.ml_utils.model.estimator import NetworkModel


client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

from abaloneage.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from abaloneage.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise PipelineException(e,sys)
    
@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        preprocesor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor, model=final_model)
        y_pred = network_model.predict(df)
        df['predicted_rings'] = y_pred
        # If actual rings/age is present, show error as well
        if 'rings' in df.columns:
            df['actual_rings'] = df['rings']
            df['abs_error'] = abs(df['predicted_rings'] - df['actual_rings'])
        if not os.path.exists('prediction_output'):
            os.makedirs('prediction_output')
        df.to_csv('prediction_output/output.csv', index=False)
        table_html = df.to_html(classes='table table-striped')
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
            raise PipelineException(e,sys)

    
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8080)
