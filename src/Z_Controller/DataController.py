from flask import Blueprint, request, jsonify
from Z_Services.DataServices import *
from Z_Services.UserServices import checkToken,checkAdmin
from Z_Services.ImageServices import deleteImage
from Z_Services.TextServices import deleteText
from pymongo.errors import PyMongoError
data_blueprint = Blueprint('data',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@data_blueprint.before_request
def dataBeforeRequest(): #Check token người dùng
    access_token = request.headers.get('Authorization')
    if not access_token:
        return 'No access token in header', 401
    try:
        checkToken(access_token)
    except Exception as e:
        print(e)
        return str(e), 401

@data_blueprint.get('/')
def getAllData():
    try:
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token):
            res = findAllData()
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500
@data_blueprint.get('/<id>')
def getDataID(id):
    try:
        access_token = request.headers.get('Authorization')
        res = findDataByID(id)
        if res[0]['uploaderID'] != checkToken(access_token)[0] and not checkAdmin(access_token): 
            return 'Forbidden', 403
        return res
    except Exception as e:
        print(e)
        return str(e), 500

@data_blueprint.post('/')
def insertDataInstance():
    try:
        data = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not data:
            return jsonify({"error": "Bad Request"}), 400
        
        #Trường Required
        if 'uploaderID' not in data or 'type' not in data or 'uploadTime' not in data: 
            return jsonify({"error": "Missing Required Values"}), 400 
        
        #Đảm bảo các trường có đúng không
        for key in data.keys():
            if key not in ["segmentID","uploaderID","type","InfoID","uploadTime","processed","processed_time","TrainValTest","location"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        res = insertData(data)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@data_blueprint.put('/')
def changeDataInstance():
    try:
        print('abc')
        data = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not data:
            return jsonify({"error": "Bad Request"}), 400
        
        print(len(data["_id"]))
        if len(data["_id"])!=24:
            return jsonify({"error": "Bad Request"}), 400
        
        #Đảm bảo các trường có đúng không
        for key in data.keys():
            if key not in ["segmentID","uploaderID","type","InfoID","uploadTime","processed","processed_time","TrainValTest","location","_id"]:
                return jsonify({"error": "Wrong key provided"}), 400 

        checkData = findDataByID(data['_id'])
        if data['uploaderID'] != checkData['uploaderID']: 
            return jsonify({"error": "uploaderID is different from the original one"}), 400
        res = updateData(data)
        return res         
    except Exception as e:
        print(e)
        return str(e), 500
    
@data_blueprint.delete('/<id>')
def deleteDataID(id): #Phải xóa image, video kèm theo (nếu có) và xóa luôn status của data đó
    try:
        access_token = request.headers.get('Authorization')
        res = findDataByID(id)
        if res[0]['uploaderID'] != checkToken(access_token)[0] and not checkAdmin(access_token): 
            return 'Forbidden', 403
        if res[0]['type'] == 'text':
            deleteText(res[0]['InfoID'])
        elif res[0]['type'] == 'image':
            deleteImage(res[0]['InfoID'])
        res = deleteData(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500