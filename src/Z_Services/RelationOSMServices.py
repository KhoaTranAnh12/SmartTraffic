from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from flask import jsonify
client = TrafficMongoClient()


#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại


relationOSMTable = client.db["relationOSM"]
#["id", "type", "location", "tags", "version", "timestamp", "changeset", "uid", "user"]
def findAllRelationOSM():
    try:
        res = relationOSMTable.find()
        res = list(res)
        return res, 200
    except PyMongoError as e:
        raise e


def findRelationOSMByID(id):
    try:
        res = relationOSMTable.find_one({"id": id})
        if res == None: return {}, 200
        return res, 200
    except PyMongoError as e:
        raise e

def updateRelationOSM(body):
    try:
        res = relationOSMTable.find_one({"id": body['id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        relationOSMTable.update_one({'id': body['id']}, {"$set": body})
        del body['id']
        return body, 201
    except PyMongoError as e:
        raise e
    
