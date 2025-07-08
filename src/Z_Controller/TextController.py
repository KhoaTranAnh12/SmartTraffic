from flask import Blueprint, request, jsonify
from Z_Services.TextServices import *
from pymongo.errors import PyMongoError
text_blueprint = Blueprint('text',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@text_blueprint.before_request
def textBeforeRequest():
    print("before text")

@text_blueprint.get('/')
def getAllText():
    try:
        res = findAllText()
        return res
    except Exception as e:
        print(e)
        return str(e), 500
@text_blueprint.get('/<id>')
def getTextID(id):
    try:
        res = findTextByID(id)
        return res
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
        if 'dataID' not in text or 'source' not in text or 'content' not in text or 'encoding' not in text: 
            return jsonify({"error": "Missing Required Values"}), 400 
        
        #Đảm bảo các trường có đúng không
        for key in text.keys():
            if key not in ["dataID", "source", "content", "encoding"]:
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
            if key not in ["dataID", "source", "content", "encoding", "_id"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        res = updateText(text)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@text_blueprint.delete('/<id>')
def deleteTextID(id):
    try:
        print(len(id))
        if len(id)!=24:
            return jsonify({"error": "Bad Request"}), 400
        res = deleteText(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    