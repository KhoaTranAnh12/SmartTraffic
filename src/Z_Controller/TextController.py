from flask import Blueprint, request, jsonify
from Z_Services.TextServices import *
from Z_Services.DataServices import findDataByTextID, findDataByUploaderID
from Z_Services.UserServices import checkToken,checkAdmin
from pymongo.errors import PyMongoError
text_blueprint = Blueprint('text',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@text_blueprint.before_request
def textBeforeRequest():
    access_token = request.headers.get('Authorization')
    if not access_token:
        return 'No access token in header', 401
    try:
        checkToken(access_token)
    except Exception as e:
        print(e)
        return str(e), 401


@text_blueprint.get('/')
def getAllText():
    try:
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token): #Đã check admin.
            res = findAllText()
            return res
        else:
            return 'Forbidden', 403 
    except Exception as e:
        print(e)
        return str(e), 500
@text_blueprint.get('/<id>')
def getTextID(id):
    try:
        #Tìm uploader:
        uploader = findDataByTextID(id)[0]['uploaderID']
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == uploader:
            res = findTextByID(id)
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500



@text_blueprint.get('/uploader/<id>') #New, chưa thêm swagger
def getTextByUploaderID(id):
    try:
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == id:
            #Services chỉ có Data theo uploader mà thôi. Ta tìm data sau đó lọc để tìm text.
            dataList = findDataByUploaderID(id)
            idList = []
            for data in dataList[0]:
                if data['type'] == 'text':
                    idList.append(str(data['_id']))
            res = findTextByDataIDList(idList)
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500

@text_blueprint.post('/')
def insertTextInstance():
    try:
        text = request.get_json()
        print(text)
        #Kiểm tra sự tồn tại của body
        if not text:
            return jsonify({"error": "Bad Request"}), 400
        #["dataID", "source", "length", "contentType", "encoding"]
        #Trường Required
        if 'dataID' not in text or 'source' not in text or 'length' not in text or 'contentType' not in text or 'encoding' not in text: 
            return jsonify({"error": "Missing Required Values"}), 400 
        
        #Đảm bảo các trường có đúng không
        for key in text.keys():
            if key not in ["dataID", "source", "length", "contentType", "encoding"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        res = insertText(text)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@text_blueprint.put('/')
def changeTextInstance():
    try:
        print('abc')
        text = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not text:
            return jsonify({"error": "Bad Request"}), 400
        
        #Đảm bảo các trường có đúng không
        for key in text.keys():
            if key not in ["dataID", "source", "length", "contentType", "encoding", "_id"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        #Tìm dataID của text cũ và so sánh
        compareText = findTextByID(text['_id'])
        if compareText['dataID']!=text['dataID']:
            return jsonify({"error": "DataID is different from the original one"}), 400

        res = updateText(text)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@text_blueprint.delete('/<id>')
def deleteTextID(id):
    try:
        #Tìm uploader:
        uploader = findDataByTextID(id)[0]['uploaderID']
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == uploader:
            res = deleteText(id)
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500
    