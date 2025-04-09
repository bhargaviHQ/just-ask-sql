import os
from dotenv import load_dotenv
import pymongo

load_dotenv()

MONGO_SRV = os.getenv("MONGO_SRV")
if not MONGO_SRV:
    raise ValueError("MONGO_SRV not set in environment variables")

MONGO_CLIENT = pymongo.MongoClient(MONGO_SRV)

def get_db_collection(database=None, collection=None):
    """Get database and collection, defaulting to .env values if not specified."""
    db_name = database or os.getenv("MONGO_DATABASE")
    coll_name = collection or os.getenv("MONGO_COLLECTION")
    if not db_name or not coll_name:
        raise ValueError("Database or collection not specified in .env or query")
    return MONGO_CLIENT[db_name][coll_name]