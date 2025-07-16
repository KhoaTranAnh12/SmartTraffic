from flask import Blueprint, request, jsonify
from Z_Services.ImageServices import *
from Z_Services.DataServices import findDataByImageID, findDataByUploaderID
from Z_Services.UserServices import checkToken,checkAdmin
from pymongo.errors import PyMongoError
image_blueprint = Blueprint('image',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@image_blueprint.before_request
def imageBeforeRequest():
    access_token = request.headers.get('Authorization')
    if not access_token:
        return 'No access token in header', 401
    try:
        checkToken(access_token)
    except Exception as e:
        print(e)
        return str(e), 401


@image_blueprint.get('/')
def getAllImage():
    try:
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token): #Đã check admin.
            res = findAllImage()
            return res
        else:
            return 'Forbidden', 403 
    except Exception as e:
        print(e)
        return str(e), 500
@image_blueprint.get('/<id>')
def getImageID(id):
    try:
        #Tìm uploader:
        uploader = findDataByImageID(id)[0]['uploaderID']
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == uploader:
            res = findImageByID(id)
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500



@image_blueprint.get('/uploader/<id>') #New, chưa thêm swagger
def getImageByUploaderID(id):
    try:
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == id:
            #Services chỉ có Data theo uploader mà thôi. Ta tìm data sau đó lọc để tìm image.
            dataList = findDataByUploaderID(id) #(cursor, 200)
            idList = []
            for data in dataList[0]:
                if data['type'] == 'image':
                    idList.append(str(data['_id']))
            res = findImageByDataIDList(idList)
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500

@image_blueprint.post('/')
def insertImageInstance():
    try:
        image = request.get_json()
        print(image)
        #Kiểm tra sự tồn tại của body
        if not image:
            return jsonify({"error": "Bad Request"}), 400
        #["dataID", "source", "length", "contentType", "encoding"]
        #Trường Required
        if 'dataID' not in image or 'source' not in image or 'length' not in image or 'contentType' not in image or 'encoding' not in image: 
            return jsonify({"error": "Missing Required Values"}), 400 
        
        #Đảm bảo các trường có đúng không
        for key in image.keys():
            if key not in ["dataID", "source", "length", "contentType", "encoding"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        res = insertImage(image)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@image_blueprint.put('/')
def changeImageInstance():
    try:
        print('abc')
        image = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not image:
            return jsonify({"error": "Bad Request"}), 400
        
        #Đảm bảo các trường có đúng không
        for key in image.keys():
            if key not in ["dataID", "source", "length", "contentType", "encoding", "_id"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        #Tìm dataID của image cũ và so sánh
        compareImage = findImageByID(image['_id'])
        if compareImage['dataID']!=image['dataID']:
            return jsonify({"error": "DataID is different from the original one"}), 400

        res = updateImage(image)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@image_blueprint.delete('/<id>')
def deleteImageID(id):
    try:
        #Tìm uploader:
        uploader = findDataByImageID(id)[0]['uploaderID']
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == uploader:
            res = deleteImage(id)
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500
    