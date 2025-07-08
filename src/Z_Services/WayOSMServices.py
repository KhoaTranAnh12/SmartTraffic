from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from flask import jsonify
client = TrafficMongoClient()


#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại


wayOSMTable = client.db["wayOSM"]
#["id", "type", "location", "tags", "version", "timestamp", "changeset", "uid", "user"]
def findAllWayOSM():
    try:
        res = wayOSMTable.find()
        res = list(res)
        return res, 200
    except PyMongoError as e:
        raise e


def findWayOSMByID(id):
    try:
        res = wayOSMTable.find_one({"id": id})
        if res == None: return {}, 200
        return res, 200
    except PyMongoError as e:
        raise e

def updateWayOSM(body):
    try:
        res = wayOSMTable.find_one({"id": body['id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        wayOSMTable.update_one({'id': body['id']}, {"$set": body})
        del body['id']
        return body, 201
    except PyMongoError as e:
        raise e
    
