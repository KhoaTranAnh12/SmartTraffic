from flask import Blueprint, request, jsonify
from Z_Services.UserServices import *
from pymongo.errors import PyMongoError
user_blueprint = Blueprint('user',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@user_blueprint.before_request
def userBeforeRequest():
    pass

@user_blueprint.get('/')
def getAllUser():
    try:
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token):
            res = findAllUser()
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500
@user_blueprint.get('/<id>')
def getUserID(id):
    try:
        access_token = request.headers.get('Authorization')
        res = findUserByID(id)
        if res[0]['_id'] != checkToken(access_token)[0] and not checkAdmin(access_token): 
            return 'Forbidden', 403
        return res
    except Exception as e:
        print(e)
        return str(e), 500

@user_blueprint.post('/')
def insertUserInstance():
    try:
        user = request.get_json()
        print(user)
        #Kiểm tra sự tồn tại của body
        if not user:
            return jsonify({"error": "Bad Request"}), 400
        
        #Trường Required
        if 'fullName' not in user or 'username' not in user or 'password' not in user or 'admin' not in user: 
            return jsonify({"error": "Missing Required Values"}), 400 
        
        #Đảm bảo các trường có đúng không
        for key in user.keys():
            print(key)
            if key not in ["fullName" , "phoneNum" , "DoB" , "status" , "loginType" , "username" , "password", "email", 'admin']:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        res = insertUser(user)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@user_blueprint.put('/')
def changeUserInstance():
    try:
        print('abc')
        user = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not user:
            return jsonify({"error": "Bad Request"}), 400
        
        #Đảm bảo các trường có đúng không
        for key in user.keys():
            print(key)
            if key not in ["fullName" , "phoneNum" , "DoB" , "status" , "loginType" , "username" , "password", "email", "_id", 'admin']:
                return jsonify({"error": "Wrong key provided"}), 400 
            
        compareUser = findUserByID(user['_id'])
        if compareUser['username']!=user['username']:
            return jsonify({"error": "DataID is different from the original one"}), 400

        res = updateUser(user)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@user_blueprint.delete('/<id>')
def deleteUserID(id):
    try:
        access_token = request.headers.get('Authorization')
        user = findUserByID(id)
        if user[0]['_id'] != checkToken(access_token)[0] and not checkAdmin(access_token): 
            return 'Forbidden', 403
        res = deleteUser(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
