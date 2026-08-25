from datetime import datetime
from pymongo import MongoClient
from app.core.config import settings

# Create MongoDB client
mongo_client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=10000)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

# Collections
raw_environmental_cache = mongo_db["raw_environmental_cache"]

def init_mongo():
    # Ensure TTL index on ingested_at field (30 days = 2592000 seconds)
    raw_environmental_cache.create_index(
        "ingested_at", 
        expireAfterSeconds=2592000
    )

def save_to_environmental_cache(lat: float, lon: float, source: str, payload: dict) -> bool:
    try:
        # Standardize lat/lon coordinates to 4 decimal places for key matching
        lat_key = round(lat, 4)
        lon_key = round(lon, 4)
        raw_environmental_cache.update_one(
            {"lat": lat_key, "lon": lon_key, "source": source},
            {
                "$set": {
                    "payload": payload,
                    "ingested_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        print(f"MongoDB cache write error for {source}: {e}", flush=True)
        return False

