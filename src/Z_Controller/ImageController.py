from flask import Blueprint, request, jsonify
from Z_Services.ImageServices import *
from Z_Services.DataServices import findDataByImageID, findDataByUploaderID
from Z_Services.UserServices import checkToken,checkAdmin
from pymongo.errors import PyMongoError
import time
image_blueprint = Blueprint('image',__name__)
import os
from dotenv import load_dotenv
#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@image_blueprint.before_request
def imageBeforeRequest():
    # access_token = request.headers.get('Authorization')
    # if not access_token:
    #     return 'No access token in header', 401
    # try:
    #     checkToken(access_token)
    # except Exception as e:
    #     print(e)
    #     return str(e), 401
    pass

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
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if content_type.startswith('multipart/form-data'):

            #Lấy STORAGE từ .env
            load_dotenv()
            print(os.getenv('STORAGE'))
            
            #Lấy image upload và thông số của nó
            image_upload = request.files.get('fileUpload')
            dataID = request.form.get('dataID')
            print(dataID)
            #Lưu Source kèm timestamp tránh trùng
            imgName = f'{time.time()}' + image_upload.filename 
            source = os.getenv('STORAGE') + '/images/unverified/' + imgName
            #Lấy size
            image_upload.seek(0, os.SEEK_END)
            file_size = image_upload.tell()
            image_upload.seek(0)
            print(file_size)

            #Lấy Content Type
            contentType = image_upload.content_type
            print(contentType)

            image = {
                'dataID' : dataID,
                'source' : imgName,
                'length' : file_size,
                'contentType' : contentType,
                "encoding" : "None"
            }
            res = insertImage(image)
            image_upload.save(source)
            return res
        elif content_type == 'application/json':
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
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if content_type.startswith('multipart/form-data'):

            #Lấy STORAGE từ .env
            load_dotenv()
            print(os.getenv('STORAGE'))
            
            #Lấy image upload và thông số của nó
            image_upload = request.files.get('fileUpload')
            dataID = request.form.get('dataID')
            imgID = request.form.get('_id')

            #Lưu Source kèm timestamp tránh trùng
            imgName = f'{time.time()}' + image_upload.filename 
            source = os.getenv('STORAGE') + '/images/unverified/' + imgName
            #Lấy size
            image_upload.seek(0, os.SEEK_END)
            file_size = image_upload.tell()
            image_upload.seek(0)
            print(file_size)

            #Lấy Content Type
            contentType = image_upload.content_type
            print(contentType)

            image = {
                '_id': imgID,
                'dataID' : dataID,
                'source' : imgName,
                'length' : file_size,
                'contentType' : contentType,
                "encoding" : "None"
            }

            #Khác Insert, Xóa Image cũ rồi thêm vào image mới, tất nhiên chỉ dành cho những image chưa được verified.
            #Những Image đã được verified rồi sẽ không xóa được nữa, và muốn xóa chỉ có liên hệ hỗ trợ phía admin.
            compareImage = findImageByID(imgID)[0]
            if compareImage['dataID']!=image['dataID']:
                return jsonify({"error": "DataID is different from the original one"}), 400
            #Xóa tệp cũ
            oldSrc = os.getenv('STORAGE') + '/images/unverified/' + compareImage['source']
            print(oldSrc)
            if(os.path.exists(oldSrc)):
                os.remove(oldSrc)

            #Xử lý lưu ảnh
            res = updateImage(image)
            if res[1]==201:
                image_upload.save(source)
            return res
        elif content_type == 'application/json':
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
            compareImage = findImageByID(image['_id'])[0]
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
    