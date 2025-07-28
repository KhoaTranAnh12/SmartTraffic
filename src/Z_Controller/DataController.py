from flask import Blueprint, request, jsonify
from Z_Services.DataServices import *
from Z_Services.UserServices import checkToken,checkAdmin
from Z_Services.ImageServices import findImageByID
from Z_Services.ImageServices import deleteImage
from Z_Services.TextServices import deleteText
from pymongo.errors import PyMongoError
from EvaluationLib.main import *
from EvaluationLib.image.lib.AITest import *
data_blueprint = Blueprint('data',__name__)
from dotenv import *
import os
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
        if 'uploaderID' not in data or 'type' not in data: 
            return jsonify({"error": "Missing Required Values"}), 400 
        
        #Đảm bảo các trường có đúng không
        for key in data.keys():
            if key not in ["segmentID","uploaderID","type","InfoID","processed","processed_time","TrainValTest","location"]:
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

@data_blueprint.get('/eval/<id>')
def evaluateStatus(id):
    try:
        data = findDataByID(id)[0]
        infoID = data['InfoID']
        if data['type'] == 'image':
            img = findImageByID(infoID)[0]
            imgSrc = os.getenv('STORAGE') + '/images/unverified/' + img['source']
            print(imgSrc)
            policeEval = TestForPolices(imgSrc)
            obstaclesEval = TestForObstacles(imgSrc)
            trafficJamEval = TestForTJam(imgSrc)
            floodedEval = TestForFlooded(imgSrc)
            return ({
                "policeEval": 
                {
                    "status": policeEval[0],
                    "score": policeEval[1]
                },
                "obstaclesEval":{
                    "status": obstaclesEval[0],
                    "score": obstaclesEval[1]
                },
                "trafficJamEval": {
                    "status": trafficJamEval[0],
                    "score": trafficJamEval[1]
                },
                "floodedEval": {
                    "status": floodedEval[0],
                    "score": floodedEval[1]
                },
                "type": 'img'}, 200)
        elif data['type'] == 'text':
            data = findDataByID(id)[0]
            infoID = data['InfoID']
            policeEval = EvaluateRandomExample()
            obstaclesEval = EvaluateRandomExample()
            trafficJamEval = EvaluateRandomExample()
            floodedEval = EvaluateRandomExample()
            return ({
                "policeEval": 
                {
                    "status": policeEval[0],
                    "score": policeEval[1]
                },
                "obstaclesEval":{
                    "status": obstaclesEval[0],
                    "score": obstaclesEval[1]
                },
                "trafficJamEval": {
                    "status": trafficJamEval[0],
                    "score": trafficJamEval[1]
                },
                "floodedEval": {
                    "status": floodedEval[0],
                    "score": floodedEval[1]
                },
                "type": 'text'}, 200)
    except Exception as e:
        print(e)
        return str(e), 500
@data_blueprint.put('/autoVerify') #Cần thêm swagger
def autoVerify(type):
    try:
        print('abc')
    except Exception as e:
        print(e)
        return str(e), 500
    
@data_blueprint.put('/manualVerify') #Cần thêm swagger
def toggleManualVerify():
    try:
        #Check Admin
        access_token = request.headers.get('Authorization')
        if not checkAdmin(access_token): 
            return 'Forbidden', 403
        body = request.get_json()
        data = findDataByID(body['_id'])
        data["processed"] = not data["processed"]
        res = updateData(data)
        return res
    except Exception as e:
        print(e)
        return str(e), 500

@data_blueprint.put('/trainValTest') #Cần thêm swagger
def putTrainValTestValue():
    try:
        #Check Admin
        access_token = request.headers.get('Authorization')
        if not checkAdmin(access_token): 
            return 'Forbidden', 403
        body = request.get_json()
        data = findDataByID(body['_id'])
        data["processed"] = not data["processed"]
        res = updateData(data)
        return res
    except Exception as e:
        print(e)
        return str(e), 500