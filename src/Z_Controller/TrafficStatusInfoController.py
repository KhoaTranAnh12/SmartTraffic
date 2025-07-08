from flask import Blueprint, request, jsonify
from Z_Services.TrafficStatusInfoServices import *
from pymongo.errors import PyMongoError
trafficStatusInfo_blueprint = Blueprint('trafficStatusInfo',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@trafficStatusInfo_blueprint.before_request
def trafficStatusInfoBeforeRequest():
    print("before trafficStatusInfo")
# "TrafficStatusID", "velocity"
@trafficStatusInfo_blueprint.get('/')
def getAllTrafficStatusInfo():
    try:
        res = findAllTrafficStatusInfo()
        return res
    except Exception as e:
        print(e)
        return str(e), 500
@trafficStatusInfo_blueprint.get('/<id>')
def getTrafficStatusInfoID(id):
    try:
        res = findTrafficStatusInfoByID(id)
        return res
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
        if 'TrafficStatusID' not in trafficStatusInfo or 'velocity' not in trafficStatusInfo:   
            return jsonify({"error": "Missing Required Values"}), 400 
        
        print(len(trafficStatusInfo["_id"]))
        if len(trafficStatusInfo["_id"])!=24:
            return jsonify({"error": "Bad Request"}), 400

        #Đảm bảo các trường có đúng không
        for key in trafficStatusInfo.keys():
            if key not in ["TrafficStatusID", "velocity"]:
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
            if key not in ["AccidentFlag", "TrafficJamFlag", "PoliceFlag", "Flooded"]:
                return jsonify({"error": "Wrong key provided"}), 400 

        res = updateTrafficStatusInfo(trafficStatusInfo)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@trafficStatusInfo_blueprint.delete('/<id>')
def deleteTrafficStatusInfoID(id):
    try:
        print(len(id))
        if len(id)!=24:
            return jsonify({"error": "Bad Request"}), 400
        res = deleteTrafficStatusInfo(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500