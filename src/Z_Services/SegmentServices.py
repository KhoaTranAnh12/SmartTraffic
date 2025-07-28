from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from flask import jsonify
client = TrafficMongoClient()


#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại


segmentTable = client.db["segments"]
#["type","id","way_id","segments","tags","version","timestamp","changeset","uid","user"]:
def findAllSegment():
    try:
        res = segmentTable.find()
        res = list(res)
        return res, 200
    except PyMongoError as e:
        raise e


def findSegmentByID(id):
    try:
        res = segmentTable.find_one({"id": id})
        if res == None: return {}, 200
        return res, 200
    except PyMongoError as e:
        raise e

def updateSegment(body):
    try:
        res = segmentTable.find_one({"id": body['id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        segmentTable.update_one({'id': body['id']}, {"$set": body})
        return body, 201
    except PyMongoError as e:
        raise e
    

