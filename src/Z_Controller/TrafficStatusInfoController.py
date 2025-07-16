from flask import Blueprint, request, jsonify
from Z_Services.TrafficStatusInfoServices import *
from Z_Services.UserServices import checkAdmin, checkToken
from Z_Services.DataServices import findDataByStatusInfoID, findDataByUploaderID
from pymongo.errors import PyMongoError
trafficStatusInfo_blueprint = Blueprint('trafficStatusInfo',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@trafficStatusInfo_blueprint.before_request
def trafficStatusInfoBeforeRequest():
    #Check Access Token
    access_token = request.headers.get('Authorization')
    if not access_token:
        return 'No access token in header', 401
    try:
        checkToken(access_token)
    except Exception as e:
        print(e)
        return str(e), 401
    
# "TrafficStatusID", "velocity"
@trafficStatusInfo_blueprint.get('/')
def getAllTrafficStatusInfo():
    try:
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token):
            res = findAllTrafficStatusInfo()
            return res
        else:
            return 'Forbidden', 403 
    except Exception as e:
        print(e)
        return str(e), 500
@trafficStatusInfo_blueprint.get('/<id>')
def getTrafficStatusInfoID(id):
    try:
        #Tìm uploader:
        uploader = findDataByStatusInfoID(id)[0]['uploaderID']
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == uploader:
            res = findTrafficStatusInfoByID(id)
            return res
    except Exception as e:
        print(e)
        return str(e), 500
    

@trafficStatusInfo_blueprint.get('/uploader/<id>') #New, chưa thêm swagger
def getStatusInfoByUploaderID(id):
    try:
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == id:
            #Services chỉ có Data theo uploader mà thôi. Trong User có StatusInfoID có thể dựa vào mà tìm.
            dataList = findDataByUploaderID(id)
            print(dataList)
            res = []
            for data in dataList[0]:
                statusInfo = findTrafficStatusInfoByID(data['InfoID'])[0]
                if statusInfo != {}:
                    res.append(statusInfo)
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500

@trafficStatusInfo_blueprint.post('/')
def insertTrafficStatusInfoInstance():
    try:
        # ["AccidentFlag", "TrafficJamFlag", "PoliceFlag", "Flooded"]
        trafficStatusInfo = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not trafficStatusInfo:
            return jsonify({"error": "Bad Request"}), 400
        
        #Trường Required
        if 'velocity' not in trafficStatusInfo or 'statuses' not in trafficStatusInfo:   
            return jsonify({"error": "Missing Required Values"}), 400 
        
        print(len(trafficStatusInfo["_id"]))
        if len(trafficStatusInfo["_id"])!=24:
            return jsonify({"error": "Bad Request"}), 400

        #Đảm bảo các trường có đúng không
        for key in trafficStatusInfo.keys():
            if key not in ["statuses", "velocity"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        res = insertTrafficStatusInfo(trafficStatusInfo)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@trafficStatusInfo_blueprint.put('/')
def changeTrafficStatusInfoInstance():
    try:
        print('abc')
        trafficStatusInfo = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not trafficStatusInfo:
            return jsonify({"error": "Bad Request"}), 400
        
        #Đảm bảo các trường có đúng không
        for key in trafficStatusInfo.keys():
            if key not in ["statuses", "velocity"]:
                return jsonify({"error": "Wrong key provided"}), 400 

        compareTrafficStatusInfo = findTrafficStatusInfoByID(trafficStatusInfo['_id'])
        if compareTrafficStatusInfo['TrafficStatusID']!=trafficStatusInfo['TrafficStatusID']:
            return jsonify({"error": "TrafficStatusID is different from the original one"}), 400

        res = updateTrafficStatusInfo(trafficStatusInfo)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@trafficStatusInfo_blueprint.delete('/<id>')
def deleteTrafficStatusInfoID(id):
    try:
        uploader = findDataByStatusInfoID(id)[0]['uploaderID']
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == uploader:
            if len(id)!=24:
                return jsonify({"error": "Bad Request"}), 400
            res = deleteTrafficStatusInfo(id)
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500