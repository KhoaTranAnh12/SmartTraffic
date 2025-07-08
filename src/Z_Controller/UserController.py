from flask import Blueprint, request, jsonify
from Z_Services.UserServices import *
from pymongo.errors import PyMongoError
user_blueprint = Blueprint('user',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@user_blueprint.before_request
def userBeforeRequest():
    print("before user")

@user_blueprint.get('/')
def getAllUser():
    try:
        res = findAllUser()
        return res
    except Exception as e:
        print(e)
        return str(e), 500
@user_blueprint.get('/<id>')
def getUserID(id):
    try:
        res = findUserByID(id)
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
        if 'fullName' not in user or 'username' not in user or 'password' not in user: 
            return jsonify({"error": "Missing Required Values"}), 400 
        
        #Đảm bảo các trường có đúng không
        for key in user.keys():
            print(key)
            if key not in ["fullName" , "phoneNum" , "DoB" , "status" , "loginType" , "username" , "password", "email"]:
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
            if key not in ["fullName" , "phoneNum" , "DoB" , "status" , "loginType" , "username" , "password", "email", "_id"]:
                return jsonify({"error": "Wrong key provided"}), 400 
            

        res = updateUser(user)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@user_blueprint.delete('/<id>')
def deleteUserID(id):
    try:
        print(len(id))
        if len(id)!=24:
            return jsonify({"error": "Bad Request"}), 400
        res = deleteUser(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
