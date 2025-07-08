from flask import Blueprint, request, jsonify
from Z_Services.RelationOSMServices import *
from pymongo.errors import PyMongoError
from bson import ObjectId
relationOSM_blueprint = Blueprint('relationOSM',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.
#Insert bằng kiểu khác string đều phải thực hiện bước convert hết.

@relationOSM_blueprint.before_request
def relationOSMBeforeRequest():
    print("before relationOSM")

@relationOSM_blueprint.get('/')
def getAllRelationOSM():
    try:
        res = findAllRelationOSM()
        return res
    except Exception as e:
        print(e)
        return str(e), 500
@relationOSM_blueprint.get('/<id>')
def getRelationOSMID(id):
    try:
        res = findRelationOSMByID(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@relationOSM_blueprint.put('/')
def changeRelationOSMInstance():
    try:
        print('abc')
        relationOSM = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not relationOSM:
            return jsonify({"error": "Bad Request"}), 400
        
        #Đảm bảo các trường có đúng không
        for key in relationOSM.keys():
            if key not in ["id", "type", "members", "tags", "version", "timestamp", "changeset", "uid", "user"]:
                return jsonify({"error": "Wrong key provided"}), 400 
            

        res = updateRelationOSM(relationOSM)
        return res
    except Exception as e:
        print(e)
        return str(e), 500