from pymongo import MongoClient, UpdateOne
from app.config import Config
from pymongo.server_api import ServerApi

client = MongoClient(Config.MONGO_URI, server_api=ServerApi('1'))
db = client[Config.DB_NAME]
collection = db[Config.COLLECTION_NAME]

def upsert_courses(records):
    """Upsert course list into MongoDB by CRN."""
    ops = []
    for record in records:
        crn = record.get("CRN")
        if not crn:
            continue
        ops.append(UpdateOne(
            {"_id": crn},
            {"$set": record},
            upsert=True
        ))

    if ops:
        collection.bulk_write(ops)

def get_courses(limit: int = 20):
    docs = list(collection.find().limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs
