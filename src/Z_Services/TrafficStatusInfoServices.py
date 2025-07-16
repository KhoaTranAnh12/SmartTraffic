from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from flask import jsonify
from datetime import datetime
client = TrafficMongoClient()
# "TrafficStatusID", "velocity"

#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại

trafficStatusInfoTable = client.db["statusInfos"]

def findAllTrafficStatusInfo():
    try:
        res = trafficStatusInfoTable.find()
        res = list(res)
        for trafficStatusInfo in res:
            trafficStatusInfo['_id'] = str(trafficStatusInfo['_id'])
        return res, 200
    except PyMongoError as e:
        raise e


def findTrafficStatusInfoByID(id):
    try:
        res = trafficStatusInfoTable.find_one({"_id": ObjectId(id)})
        if res == None: return {}, 200
        res['_id'] = str(res['_id'])
        return res, 200
    except PyMongoError as e:
        raise e


def insertTrafficStatusInfo(body):
    try:
        trafficStatusInfoTable.insert_one(body)
        del body['_id']
        return body, 201
    except PyMongoError as e:
        raise e
def updateTrafficStatusInfo(body):
    try:
        body['_id'] = ObjectId(body['_id'])
        res = trafficStatusInfoTable.find_one({"_id": body['_id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        trafficStatusInfoTable.update_one({'_id': body['_id']}, {"$set": body})
        del body['_id']
        return body, 201
    except PyMongoError as e:
        raise e

def deleteTrafficStatusInfo(id):
    try:
        res = trafficStatusInfoTable.find_one({"_id": ObjectId(id)})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        res = trafficStatusInfoTable.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Successful"}), 200
    except PyMongoError as e:
        raise e