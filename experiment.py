import pymongo
import sys
from pymongo.errors import PyMongoError

def func():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["test"]
    coll = db['data']
    res = coll.insert_one({})


try:
    func()
except Exception as e:
    print(type(e) is PyMongoError)