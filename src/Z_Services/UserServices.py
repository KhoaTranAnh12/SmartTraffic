from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from flask import jsonify
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import hmac
import hashlib
import base64
import bcrypt
from flask_jwt_extended import decode_token
from jwt.exceptions import InvalidTokenError

client = TrafficMongoClient()
from flask_jwt_extended import (
    create_access_token, create_refresh_token
)

#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại

userTable = client.db["users"]
refreshTokenTable = client.db['refreshTokens']

def hashPassword(username,password):
    load_dotenv()
    secretKey = os.getenv('SECRET')
    key = hmac.new(secretKey.encode('utf-8'),username.encode('utf-8') + password.encode('utf-8'),hashlib.sha256).digest()
    # print(f'key {key}')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(key,salt)
    return hashed.decode('utf-8')

def checkPassword(username,password,checkhash):
    load_dotenv()
    secretKey = os.getenv('SECRET')
    key = hmac.new(secretKey.encode('utf-8'),username.encode('utf-8') + password.encode('utf-8'),hashlib.sha256).digest()
    return bcrypt.checkpw(key,checkhash.encode('utf-8'))


def checkToken(accessTok):
    try:
        decoded = decode_token(accessTok)  # Tự động xác minh chữ ký và thời gian hết hạn
        print("Token hợp lệ:", decoded)
        id = decoded['sub'] #Lấy identity
        if findUserByID(id)[0]!={}:
            return id, 201
        else:
            raise "Invalid Token!"
    except InvalidTokenError as e:
        print("Token không hợp lệ:", str(e))
        raise e
    
def checkAdmin(accessTok):
    try:
        decoded = decode_token(accessTok)  # Tự động xác minh chữ ký và thời gian hết hạn
        print("Token hợp lệ:", decoded)
        id = decoded['sub'] #Lấy identity
        user = findUserByID(id)[0]
        if user != {}:
            if user['admin']: return True
        else:
            return False
    except InvalidTokenError as e:
        print("Token không hợp lệ:", str(e))
        raise e

def login(body):
    try:
        account = userTable.find_one({"username": body["username"]})
        if account == None: return 'Invalid Username and Password!', 400
        if checkPassword(body['username'],body['password'],account['password']):
            access_token = create_access_token(identity=str(account["_id"]))
            refresh_token = create_refresh_token(identity=str(account["_id"]))
            refreshTokenTable.insert_one({
                "token": refresh_token,
                "userID": account["_id"],
                "expiredAt": datetime.now() + timedelta(days=7)
            })
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        else:
            return 'Invalid Username and Password!', 400
    except PyMongoError as e:
        raise e
    
def refreshToken(body):
    try:
        refresh_token =  refreshTokenTable.find_one({
            "token": body["token"],
            "userID": body["_id"],
            "expiredAt": {'$gt': datetime.now()}
        })
        if refresh_token:
            access_token = create_access_token(identity=body["username"])
            return jsonify({'access_token': access_token}), 200
        else:
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
    except PyMongoError as e:
        raise e 

def findAllUser():
    try:
        res = userTable.find()
        res = list(res)
        for user in res:
            user['_id'] = str(user['_id'])
        return res, 200
    except PyMongoError as e:
        raise e


def findUserByID(id):
    try:
        res = userTable.find_one({"_id": ObjectId(id)})
        if res == None: return {}, 200
        res['_id'] = str(res['_id'])
        return res, 200
    except PyMongoError as e:
        raise e

def findUserByUsername(username):
    try:
        print(username)
        res = userTable.find_one({"username": username})
        if res == None: return {"msg": "Not found"}, 404
        res['_id'] = str(res['_id'])
        return res, 200
    except PyMongoError as e:
        raise e


def insertUser(body):
    try:
        if body['DoB']: body["DoB"] = datetime.strptime(body["DoB"],"%Y/%m/%d")
        else: body["DoB"] = None
        if not body['email']: body['email'] = None
        if not body['phoneNum']: body['phoneNum'] = None
        if not body['status']: body['phoneNum'] = True
        if not body['loginType']: body['loginType'] = None
        body["password"] = hashPassword(body["username"],body["password"])
        userTable.insert_one(body)
        del body['_id']
        return body, 201
    except PyMongoError as e:
        raise e
def updateUser(body):
    try:
        if body['DoB']: body["DoB"] = datetime.strptime(body["DoB"],"%Y/%m/%d")
        body['_id'] = ObjectId(body['_id'])
        body["password"] = hashPassword(body["username"],body["password"])
        res = userTable.find_one({"_id": body['_id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 40
        userTable.update_one({'_id': body['_id']}, {"$set": body})
        del body['_id']
        return body, 201
    except PyMongoError as e:
        raise e

def deleteUser(id):
    try:
        res = userTable.find_one({"_id": ObjectId(id)})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        res = userTable.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Successful"}), 200
    except PyMongoError as e:
        raise e