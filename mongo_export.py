import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
DATABASE = "abalone_db"
COLLECTION = "abalone"
EXPORT_PATH = "Abalone_Data/abalone.csv"

if not MONGO_DB_URL:
    raise ValueError("MONGO_DB_URL environment variable not set.")

client = MongoClient(MONGO_DB_URL)
db = client[DATABASE]
collection = db[COLLECTION]

# Fetch all documents
records = list(collection.find())
if not records:
    raise ValueError("No records found in MongoDB collection.")

# Remove MongoDB _id field
for rec in records:
    rec.pop('_id', None)

# Convert to DataFrame and export
pd.DataFrame(records).to_csv(EXPORT_PATH, index=False)
print(f"Exported {len(records)} records to {EXPORT_PATH}")
