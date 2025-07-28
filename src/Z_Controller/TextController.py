from flask import Blueprint, request, jsonify
from Z_Services.TextServices import *
from Z_Services.DataServices import findDataByTextID, findDataByUploaderID,findDataByID,updateData
from Z_Services.UserServices import checkToken,checkAdmin,findUserByUsername
from pymongo.errors import PyMongoError
import time
import os
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



@text_blueprint.get('/uploader/<username>') #New, chưa thêm swagger
def getTextByUploaderUsername(username):
    try:
        userID = findUserByUsername(username)[0]['_id']
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == userID:
            #Services chỉ có Data theo uploader mà thôi. Ta tìm data sau đó lọc để tìm text.
            dataList = findDataByUploaderID(userID)
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
        if 'dataID' not in text or 'content' not in text: 
            return jsonify({"error": "Missing Required Values"}), 400 
        
        #Đảm bảo các trường có đúng không
        for key in text.keys():
            if key not in ["dataID", "content"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        #Xử lý viết file vào storage
        fileName = f'text_{time.time()}.txt'
        data = findDataByID(text['dataID'])[0]
        print(data)
        if data['type'] != 'text': return {'error': 'Wrong Data Type!'}, 400
        #Đưa vào db
        inputDb = {
            "dataID" : text['dataID'],
            'source': fileName
        }
        res = insertText(inputDb)
        print(res)
        data['InfoID'] = res[0]['_id']
        print(data)
        updateData(data)
        #Xử lý viết file vào storage
        if res[1]==200:
            source = os.getenv('STORAGE') + '/texts/unverified/' + fileName
            print(source)
            with open(source, 'w') as f:
                f.write(text['content'])
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
            if key not in ["_id","dataID", "content"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        #Tìm dataID của text cũ và so sánh
        compareText = findTextByID(text['_id'])[0]
        print(compareText)
        if compareText['dataID']!=text['dataID']:
            return jsonify({"error": "DataID is different from the original one"}), 400

        #Xoá tệp cũ
        oldfileName = os.getenv('STORAGE') + '/texts/unverified/' + compareText['source']
        if(os.path.exists(oldfileName)):
            os.remove(oldfileName)
            
        #Xử lý viết file vào storage
        fileName = f'text_{time.time()}.txt'

        #Đưa vào db
        inputDb = {
            '_id': text['_id'],
            "dataID" : text['dataID'],
            'source': fileName
        }
        res = updateText(inputDb)
        #Xử lý viết file vào storage
        if res[1]==201:
            source = os.getenv('STORAGE') + '/texts/unverified/' + fileName
            print(source)
            with open(source, 'w') as f:
                f.write(text['content'])
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
    