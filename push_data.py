import os
import sys
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv not available or .env not present; continue relying on env vars
    pass

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

try:
    import certifi
    ca = certifi.where()
except Exception:
    ca = None

import pandas as pd
import numpy as np
import pymongo
import logging


class PipelineException(Exception):
    def __init__(self, error, sys_module=None):
        super().__init__(str(error))

class AbaloneDataExtract:
    """Helper to convert Abalone CSV to JSON records and insert into MongoDB."""
    def __init__(self, mongo_uri: str = None):
        try:
            self.mongo_uri = mongo_uri or MONGO_DB_URL
        except Exception as e:
            raise PipelineException(e, sys)

    def csv_to_json_convertor(self, file_path: str):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise PipelineException(e, sys)

    def insert_data_mongodb(self, records, database: str, collection: str):
        try:
            if not self.mongo_uri:
                raise PipelineException(
                    "MONGO_DB_URL is not set. Set the environment variable MONGO_DB_URL to your MongoDB URI or start a local MongoDB instance and set MONGO_DB_URL=mongodb://localhost:27017"
                )

            client = pymongo.MongoClient(self.mongo_uri)
            db = client[database]
            coll = db[collection]
            coll.insert_many(records)
            return len(records)
        except Exception as e:
            raise PipelineException(e, sys)
        
if __name__ == '__main__':
    FILE_PATH = os.path.join("Abalone_Data", "abalone.csv")
    DATABASE = "abalone_db"
    Collection = "abalone"
    extractor = AbaloneDataExtract()
    records = extractor.csv_to_json_convertor(file_path=FILE_PATH)
    no_of_records = extractor.insert_data_mongodb(records, DATABASE, Collection)
    print(f"Inserted {no_of_records} records into {DATABASE}.{Collection}")
        


