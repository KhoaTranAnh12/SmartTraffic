from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from flask import jsonify
from datetime import datetime
client = TrafficMongoClient()


#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại

textTable = client.db["texts"]

def findAllText():
    try:
        #["dataID", "source", "length", "contentType", "encoding"]:
        res = textTable.find()
        res = list(res)
        for text in res:
            text['_id'] = str(text['_id'])
            text['dataID'] = str(text['dataID'])
        return res, 200
    except PyMongoError as e:
        raise e


def findTextByID(id):
    try:
        res = textTable.find_one({"_id": ObjectId(id)})
        if res == None: return {}, 200
        res['_id'] = str(res['_id'])
        res['dataID'] = str(res['dataID'])
        return res, 200
    except PyMongoError as e:
        raise e

def insertText(body):
    try:
        body['dataID'] = ObjectId(body['dataID'])
        textTable.insert_one(body)
        del body['_id']
        body['dataID'] = str(body['dataID'])
        return body, 201
    except PyMongoError as e:
        raise e
def updateText(body):
    try:
        body['_id'] = ObjectId(body['_id'])
        body['dataID'] = ObjectId(body['dataID'])
        res = textTable.find_one({"_id": body['_id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        
        textTable.update_one({'_id': body['_id']}, {"$set": body})
        del body['_id']
        body['dataID'] = str(body['dataID'])
        return body, 201
    except PyMongoError as e:
        raise e

def deleteText(id):
    try:
        res = textTable.find_one({"_id": ObjectId(id)})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        res = textTable.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Successful"}), 200
    except PyMongoError as e:
        raise e