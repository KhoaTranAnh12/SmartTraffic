from flask import Blueprint, request, jsonify
from Z_Services.ImageServices import *
from pymongo.errors import PyMongoError
image_blueprint = Blueprint('image',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@image_blueprint.before_request
def imageBeforeRequest():
    print("before image")

@image_blueprint.get('/')
def getAllImage():
    try:
        res = findAllImage()
        return res
    except Exception as e:
        print(e)
        return str(e), 500
@image_blueprint.get('/<id>')
def getImageID(id):
    try:
        res = findImageByID(id)
        return res
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
        if 'dataID' not in image or 'source' not in image or 'length' not in image or 'contentType' not in image or 'encoding'not in image: 
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
        
        res = updateImage(image)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@image_blueprint.delete('/<id>')
def deleteImageID(id):
    try:
        print(len(id))
        if len(id)!=24:
            return jsonify({"error": "Bad Request"}), 400
        res = deleteImage(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    