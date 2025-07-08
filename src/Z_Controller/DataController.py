from flask import Blueprint, request, jsonify
from Z_Services.DataServices import *
from pymongo.errors import PyMongoError
data_blueprint = Blueprint('data',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@data_blueprint.before_request
def dataBeforeRequest():
    print("before data")

@data_blueprint.get('/')
def getAllData():
    try:
        res = findAllData()
        return res
    except Exception as e:
        print(e)
        return str(e), 500
@data_blueprint.get('/<id>')
def getDataID(id):
    try:
        res = findDataByID(id)
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

        res = updateData(data)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@data_blueprint.delete('/<id>')
def deleteDataID(id):
    try:
        print(len(id))
        if len(id)!=24:
            return jsonify({"error": "Bad Request"}), 400
        res = deleteData(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500