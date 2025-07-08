from flask import Blueprint, request, jsonify
from Z_Services.WayOSMServices import *
from pymongo.errors import PyMongoError
from bson import ObjectId
wayOSM_blueprint = Blueprint('wayOSM',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.
#Insert bằng kiểu khác string đều phải thực hiện bước convert hết.

@wayOSM_blueprint.before_request
def wayOSMBeforeRequest():
    print("before wayOSM")

@wayOSM_blueprint.get('/')
def getAllWayOSM():
    try:
        res = findAllWayOSM()
        return res
    except Exception as e:
        print(e)
        return str(e), 500
@wayOSM_blueprint.get('/<id>')
def getWayOSMID(id):
    try:
        res = findWayOSMByID(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@wayOSM_blueprint.put('/')
def changeWayOSMInstance():
    try:
        print('abc')
        wayOSM = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not wayOSM:
            return jsonify({"error": "Bad Request"}), 400
        
        #Đảm bảo các trường có đúng không
        for key in wayOSM.keys():
            if key not in ["id", "type", "nodes", "tags", "version", "timestamp", "changeset", "uid", "user"]:
                return jsonify({"error": "Wrong key provided"}), 400 
            

        res = updateWayOSM(wayOSM)
        return res
    except Exception as e:
        print(e)
        return str(e), 500