from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from datetime import datetime
from flask import jsonify
client = TrafficMongoClient()


#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại

dataTable = client.db["data"]

def findAllData():
    try:
        res = dataTable.find()
        res = list(res)
        for data in res:
            data['_id'] = str(data['_id'])
            data['uploaderID'] = str(data['uploaderID'])
            data['InfoID'] = str(data['InfoID'])
        return res, 200
    except PyMongoError as e:
        raise e


def findDataByID(id):
    try:
        res = dataTable.find_one({"_id": ObjectId(id)})
        if res == None: return {}, 200
        res['_id'] = str(res['_id'])
        res['uploaderID'] = str(res['uploaderID'])
        res['InfoID'] = str(res['InfoID'])
        return res, 200
    except PyMongoError as e:
        raise e

def insertData(body):
    try:

        body['uploaderID'] = ObjectId(body['uploaderID'])
        body['InfoID'] = ObjectId(body['InfoID'])
        body["uploadTime"] = datetime.strptime(body["uploadTime"],"%Y/%m/%d")
        dataTable.insert_one(body)
        del body['_id']
        body['uploaderID'] = str(body['uploaderID'])
        body['InfoID'] = str(body['InfoID'])
        return body, 201
    except PyMongoError as e:
        raise e
def updateData(body):
    try:

        body['uploaderID'] = ObjectId(body['uploaderID'])
        body['InfoID'] = ObjectId(body['InfoID'])
        body["uploadTime"] = datetime.strptime(body["uploadTime"],"%Y/%m/%d")
        body['_id'] = ObjectId(body['_id'])
        res = dataTable.find_one({"_id": body['_id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        dataTable.update_one({'_id': body['_id']}, {"$set": body})
        del body['_id']
        body['uploaderID'] = str(body['uploaderID'])
        body['InfoID'] = str(body['InfoID'])
        return body, 201
    except PyMongoError as e:
        raise e

def deleteData(id):
    try:
        res = dataTable.find_one({"_id": ObjectId(id)})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        res = dataTable.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Succesful"}), 200
    except PyMongoError as e:
        raise e