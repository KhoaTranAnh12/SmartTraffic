from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from datetime import datetime
from flask import jsonify
client = TrafficMongoClient()


#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại

reportTable = client.db["report"]


def findAllReport():
    try:
        res = reportTable.find()
        res = list(res)
        for report in res:
            report['_id'] = str(report['_id'])
            report['uploaderID'] = str(report['uploaderID'])
            report['dataTextID'] = str(report['dataTextID'])
            report['dataImgID'] = str(report['dataImgID'])
        return res, 200
    except PyMongoError as e:
        raise e


def findReportByID(id):
    try:
        res = reportTable.find_one({"_id": ObjectId(id)})
        
        if res == None: return {}, 200
        res['_id'] = str(res['_id'])
        res['uploaderID'] = str(res['uploaderID'])
        res['dataTextID'] = str(res['dataTextID'])
        res['dataImgID'] = str(res['dataImgID'])
        print(res)
        return res, 200
    except PyMongoError as e:
        raise e

def findReportByUploaderID(id):
    try:
        res = reportTable.find({"uploaderID": ObjectId(id)})
        if res == None: return {}, 200
        res=list(res)
        for report in res:
            report['_id'] = str(report['_id'])
            report['uploaderID'] = str(report['uploaderID'])
            report['dataTextID'] = str(report['dataTextID'])
            report['dataImgID'] = str(report['dataImgID'])
        return res, 200
    except PyMongoError as e:
        raise e
    
def findReportByDataImageID(id):
    try:
        res = reportTable.find_one({"dataImgID": ObjectId(id)})
        if res == None: return {}, 200
        res['_id'] = str(res['_id'])
        res['uploaderID'] = str(res['uploaderID'])
        res['dataTextID'] = str(res['dataTextID'])
        res['dataImgID'] = str(res['dataImgID'])
        return res, 200
    except PyMongoError as e:
        raise e
    
def findReportDataTextID(id):
    try:
        res = reportTable.find_one({"dataTextID": ObjectId(id)})
        if res == None: return {}, 200
        res['_id'] = str(res['_id'])
        res['uploaderID'] = str(res['uploaderID'])
        res['dataTextID'] = str(res['dataTextID'])
        res['dataImgID'] = str(res['dataImgID'])
        return res, 200
    except PyMongoError as e:
        raise e


def insertReport(body):
    try:
        body['uploaderID'] = ObjectId(body['uploaderID'])
        body['textID'] = None
        body['imageID'] = None
        body["eval"] = 0
        body['qualified'] = False
        body['createdDate'] = datetime.today()
        reportTable.insert_one(body)
        body['_id'] = str(body['_id'])
        body['uploaderID'] = str(body['uploaderID'])
        body['dataTextID'] = str(body['dataTextID'])
        body['dataImgID'] = str(body['dataImgID'])
        return body, 201
    except PyMongoError as e:
        raise e
def updateReport(body):
    try:
        print(body)
        body['uploaderID'] = ObjectId(body['uploaderID'])
        body['textID'] = ObjectId(body['textID'])
        body['imageID'] = ObjectId(body['imageID'])
        body['_id'] = ObjectId(body['_id'])
        res = reportTable.find_one({"_id": body['_id']})
        print('abc')
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        print(body)
        reportTable.update_one({'_id': body['_id']}, {"$set": body})
        print('a')
        body['_id'] = str(body['_id'])
        body['uploaderID'] = str(body['uploaderID'])
        body['dataTextID'] = str(body['dataTextID'])
        body['dataImgID'] = str(body['dataImgID'])
        print(body)
        return body, 201
    except PyMongoError as e:
        raise e

def deleteReport(id):
    try:
        res = reportTable.find_one({"_id": ObjectId(id)})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        res = reportTable.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Successful"}), 200
    except PyMongoError as e:
        raise e