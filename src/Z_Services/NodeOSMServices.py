from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from pymongo import GEOSPHERE
from bson.objectid import ObjectId
from flask import jsonify
client = TrafficMongoClient()


#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại


nodeOSMTable = client.db["nodes"]
#["id", "type", "location", "tags", "version", "timestamp", "changeset", "uid", "user"]
def findAllNodeOSM():
    try:
        res = nodeOSMTable.find()
        res = list(res)
        for i in res:
            del i['_id']
        return res, 200
    except PyMongoError as e:
        raise e

def findNodeOSMbyCoor(a,b):
    try:
        print(a,b)
        res = nodeOSMTable.find_one({
            "type": "node",
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [a, b]
                    },
                    "$maxDistance": 1000  # Giới hạn bán kính 1000 mét
                }
            }
        })
        if res == None: return {}, 200
        del res['_id']
        return res, 200
    except PyMongoError as e:
        raise e

def findNodeOSMInSegmentbyCoor(a,b):
    try:
        print(a,b)
        res = nodeOSMTable.find_one({
            "type": "node",
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [a, b]
                    },
                    "$maxDistance": 1000  # Giới hạn bán kính 1000 mét
                }
            },
            "belongs_to_segments": {"$exists": True, "$ne": []}
        })
        if res == None: return {}, 200
        del res['_id']
        return res, 200
    except PyMongoError as e:
        raise e

def findNodeOSMByID(id):
    try:
        res = nodeOSMTable.find_one({"id": id})
        if res == None: return {}, 200
        del res['_id']
        return res, 200
    except PyMongoError as e:
        raise e

def updateNodeOSM(body):
    try:
        res = nodeOSMTable.find_one({"id": body['id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        nodeOSMTable.update_one({'id': body['id']}, {"$set": body})
        del res['_id']
        return res, 201
    except PyMongoError as e:
        raise e
    

