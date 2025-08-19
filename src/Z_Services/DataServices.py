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

def findDataByUploaderID(id):
    try:
        res = dataTable.find({"uploaderID": ObjectId(id)})
        if res == None: return {}, 200
        res=list(res)
        for data in res:
            data['_id'] = str(data['_id'])
            data['uploaderID'] = str(data['uploaderID'])
            data['InfoID'] = str(data['InfoID'])
        return res, 200
    except PyMongoError as e:
        raise e
    
def findDataByStatusInfoID(id):
    try:
        res = dataTable.find({"InfoID": ObjectId(id)})
        if res == None: return {}, 200
        res=list(res)
        for data in res:
            data['_id'] = str(data['_id'])
            data['uploaderID'] = str(data['uploaderID'])
            data['InfoID'] = str(data['InfoID'])
        return res, 200
    except PyMongoError as e:
        raise e

def findDataByImageID(id):
    try:
        res = dataTable.find_one({"infoID": ObjectId(id), "type": 'image'})
        if res == None: return {}, 200
        res['_id'] = str(res['_id'])
        res['uploaderID'] = str(res['uploaderID'])
        res['InfoID'] = str(res['InfoID'])
        return res, 200
    except PyMongoError as e:
        raise e
    
def findDataByTextID(id):
    try:
        res = dataTable.find_one({"infoID": ObjectId(id), "type": 'text'})
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
        if 'InfoID' not in body: body['InfoID'] = None
        if 'reportID' not in body: body['reportID'] = None
        if 'uploadTime' not in body: body["uploadTime"] = datetime.today()
        if 'processed' not in body: body['processed'] = False
        if 'processed_time' not in body: body['processed_time'] = None
        if 'TrainValTest' not in body: body['TrainValTest'] = 0
        if 'location' not in body: body['location'] = None
        dataTable.insert_one(body)
        body['_id']= str(body['_id'])
        body['uploaderID'] = str(body['uploaderID'])
        body['InfoID'] = str(body['InfoID'])
        return body, 201
    except PyMongoError as e:
        raise e
def updateData(body):
    try:
        body['uploaderID'] = ObjectId(body['uploaderID'])
        body['InfoID'] = ObjectId(body['InfoID'])
        body['reportID'] = ObjectId(body['reportID'])
        body["uploadTime"] = datetime.today()
        body['_id'] = ObjectId(body['_id'])
        res = dataTable.find_one({"_id": body['_id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        dataTable.update_one({'_id': body['_id']}, {"$set": body})
        body['uploaderID'] = str(body['uploaderID'])
        body['InfoID'] = str(body['InfoID'])
        body['_id'] = str(body['_id'])
        return body, 201
    except PyMongoError as e:
        raise e

def deleteData(id):
    try:
        res = dataTable.find_one({"_id": ObjectId(id)})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        res = dataTable.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Successful"}), 200
    except PyMongoError as e:
        raise e
    
def convert_obj(doc):
    if isinstance(doc, list):
        return [convert_obj(d) for d in doc]
    elif isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                new_doc[k] = str(v)
            elif isinstance(v, datetime):
                new_doc[k] = v.isoformat()
            else:
                new_doc[k] = convert_obj(v)
        return new_doc
    else:
        return doc