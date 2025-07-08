from flask import Blueprint, request, jsonify
from Z_Services.NodeOSMServices import *
from pymongo.errors import PyMongoError
from bson import ObjectId
nodeOSM_blueprint = Blueprint('nodeOSM',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.
#Insert bằng kiểu khác string đều phải thực hiện bước convert hết.

@nodeOSM_blueprint.before_request
def nodeOSMBeforeRequest():
    print("before nodeOSM")

@nodeOSM_blueprint.get('/')
def getAllNodeOSM():
    try:
        res = findAllNodeOSM()
        return res
    except Exception as e:
        print(e)
        return str(e), 500
@nodeOSM_blueprint.get('/<id>')
def getNodeOSMID(id):
    try:
        res = findNodeOSMByID(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@nodeOSM_blueprint.put('/')
def changeNodeOSMInstance():
    try:
        print('abc')
        nodeOSM = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not nodeOSM:
            return jsonify({"error": "Bad Request"}), 400
        
        #Đảm bảo các trường có đúng không
        for key in nodeOSM.keys():
            if key not in ["id", "type", "location", "tags", "version", "timestamp", "changeset", "uid", "user"]:
                return jsonify({"error": "Wrong key provided"}), 400 
            

        res = updateNodeOSM(nodeOSM)
        return res
    except Exception as e:
        print(e)
        return str(e), 500