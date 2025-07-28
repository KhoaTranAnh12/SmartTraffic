from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from flask import jsonify
from datetime import datetime
client = TrafficMongoClient()


#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại

imageTable = client.db["images"]

def findAllImage():
    try:
        #["dataID", "source", "length", "contentType", "encoding"]:
        res = imageTable.find()
        res = list(res)
        for image in res:
            image['_id'] = str(image['_id'])
            image['dataID'] = str(image['dataID'])
        return res, 200
    except PyMongoError as e:
        raise e


def findImageByID(id):
    try:
        res = imageTable.find_one({"_id": ObjectId(id)})
        if res == None: return {}, 200
        res['_id'] = str(res['_id'])
        res['dataID'] = str(res['dataID'])
        return res, 200
    except PyMongoError as e:
        raise e

def findImageByDataIDList(idlist):
    try:
        objList = []
        for dataID in idlist: objList.append(ObjectId(dataID))
        res = imageTable.find({"dataID": {'$in': objList}})
        if res == None: return {}, 200
        res = list(res)
        for img in res:
            img['_id'] = str(img['_id'])
            img['dataID'] = str(img['dataID'])
        return res, 200
    except PyMongoError as e:
        raise e

def insertImage(body):
    try:
        body['dataID'] = ObjectId(body['dataID'])
        imageTable.insert_one(body)
        body['_id'] = str(body['_id'])
        body['dataID'] = str(body['dataID'])
        return body, 201
    except PyMongoError as e:
        raise e
def updateImage(body):
    try:
        body['_id'] = ObjectId(body['_id'])
        body['dataID'] = ObjectId(body['dataID'])
        res = imageTable.find_one({"_id": body['_id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        
        imageTable.update_one({'_id': body['_id']}, {"$set": body})
        del body['_id']
        body['dataID'] = str(body['dataID'])
        return body, 201
    except PyMongoError as e:
        raise e

def deleteImage(id):
    try:
        res = imageTable.find_one({"_id": ObjectId(id)})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        res = imageTable.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Successful"}), 200
    except PyMongoError as e:
        raise e