from pymongo import MongoClient
from bson.objectid import ObjectId
import asyncio
import platform

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['test']

# Collection names
provinces_collection = db['provinces']
cities_collection = db['cities']
wards_collection = db['wards']

async def main():
    # Insert Province (TP.HCM)
   

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())