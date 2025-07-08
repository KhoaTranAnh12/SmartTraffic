from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from flask import jsonify
client = TrafficMongoClient()


#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại


notificationsTable = client.db["notifications"]

def findAllNotifications():
    try:
        res = notificationsTable.find()
        res = list(res)
        for notification in res:
            notification['_id'] = str(notification['_id'])
            notification['userID'] = str(notification['userID'])
        return res, 200
    except PyMongoError as e:
        raise e


def findNotificationsByID(id):
    try:
        res = notificationsTable.find_one({"_id": ObjectId(id)})
        if res == None: return {}, 200
        res['_id'] = str(res['_id'])
        res['userID'] = str(res['userID'])
        return res, 200
    except PyMongoError as e:
        raise e

def insertNotifications(body):
    try:
        
        body['userID'] = ObjectId(body['userID'])
        notificationsTable.insert_one(body)
        del body['_id']
        body['userID'] = str(body['userID'])
        return body, 201
    except PyMongoError as e:
        raise e
def updateNotifications(body):
    try:
        body['userID'] = ObjectId(body['userID'])
        body['_id'] = ObjectId(body['_id'])
        res = notificationsTable.find_one({"_id": body['_id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        notificationsTable.update_one({'_id': body['_id']}, {"$set": body})
        del body['_id']
        body['userID'] = str(body['userID'])
        return body, 201
    except PyMongoError as e:
        raise e

def deleteNotifications(id):
    try:
        res = notificationsTable.find_one({"_id": ObjectId(id)})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        res = notificationsTable.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Succesful"}), 200
    except PyMongoError as e:
        raise e