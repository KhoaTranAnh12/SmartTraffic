from flask import Blueprint, request, jsonify
from Z_Services.DataServices import *
from Z_Services.UserServices import checkToken,checkAdmin
from Z_Services.ImageServices import findImageByID, insertImage
from Z_Services.ImageServices import deleteImage
from Z_Services.TextServices import deleteText, insertText
from pymongo.errors import PyMongoError
from EvaluationLib.main import *
from EvaluationLib.image.lib.AITest import *
data_blueprint = Blueprint('data',__name__)
from dotenv import *
import os
import time
#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@data_blueprint.before_request
def dataBeforeRequest(): #Check token người dùng
    access_token = request.headers.get('Authorization')
    if not access_token:
        return 'No access token in header', 401
    try:
        checkToken(access_token)
    except Exception as e:
        print(e)
        return str(e), 401

@data_blueprint.get('/')
def getAllData():
    try:
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token):
            res = findAllData()
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500
@data_blueprint.get('/<id>')
def getDataID(id):
    try:
        access_token = request.headers.get('Authorization')
        res = findDataByID(id)
        if res[0]['uploaderID'] != checkToken(access_token)[0] and not checkAdmin(access_token): 
            return 'Forbidden', 403
        return res
    except Exception as e:
        print(e)
        return str(e), 500

@data_blueprint.post('/')
def insertDataInstance():
    try:
        data = request.get_json()
        #Kiểm tra sự tồn tại của body
        if not data:
            return jsonify({"error": "Bad Request"}), 400
        
        #Nếu k có uploaderID, sử dụng check auth.
        if 'uploaderID' not in data:
            access_token = request.headers.get('Authorization')
            if not access_token: return jsonify({"error": "Bad Request"}), 400 
            uploaderID = checkToken(access_token)[0]
            data['uploaderID'] = uploaderID
    
        #Trường Required
        if 'type' not in data: 
            return jsonify({"error": "Missing Required Values"}), 400 
        
        #Đảm bảo các trường có đúng không
        for key in data.keys():
            if key not in ["segmentID","uploaderID","type","InfoID","processed","processed_time","TrainValTest","location"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        res = insertData(data)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@data_blueprint.post('/img')
def insertDataImageInstance():
    try:
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if request.form.get('uploaderID'): bodyUploaderID = ObjectId(request.form.get('uploaderID'))
        else:
            bodyUploaderID = None
        if not bodyUploaderID:
            access_token = request.headers.get('Authorization')
            if not access_token: return jsonify({"error": "Bad Request"}), 400 
            bodyUploaderID = checkToken(access_token)[0]
        #Phần form-data
        if content_type.startswith('multipart/form-data'):
            datajson = {
                'uploaderID' : bodyUploaderID,
                'type' : 'image'
            }
            print('abc')
            resData = insertData(datajson)[0]
            resDataID = resData['_id']
            #Xử lý phần upload
            print('abcd')
            #Lấy STORAGE từ .env
            load_dotenv()
            print(os.getenv('STORAGE'))
            #Lấy image upload và thông số của nó
            image_upload = request.files.get('fileUpload')
            dataID = resDataID
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
            data = findDataByID(resDataID)[0]
            if data['type'] != 'image': return {'error': 'Wrong Data Type!'}, 400
            res = insertImage(image)
            imgID = res[0]['_id']
            print('abc')
            data['InfoID'] = imgID
            updateData(data)
            image_upload.save(source)
            return res
        elif content_type == 'application/json':
            image = request.get_json()
            #Kiểm tra sự tồn tại của body
            if not image:
                return jsonify({"error": "Bad Request"}), 400
            if 'uploaderID' not in image:
                access_token = request.headers.get('Authorization')
                if not access_token: return jsonify({"error": "Bad Request"}), 400 
                uploaderID = checkToken(access_token)[0]
                data['uploaderID'] = uploaderID
            #Validation
            #Trường Required
            if 'uploaderID' not in image or 'source' not in image or 'length' not in image or 'contentType' not in image or 'encoding' not in image: 
                return jsonify({"error": "Missing Required Values"}), 400 
            
            #Đảm bảo các trường có đúng không
            for key in image.keys():
                if key not in ["uploaderID", "source", "length", "contentType", "encoding"]:
                    return jsonify({"error": "Wrong key provided"}), 400 
                
            datajson = {
                'uploaderID' : image['uploaderID'],
                'type' : 'image'
            }

            resData = insertData(datajson)[0]
            resDataID = resData['_id']

            imgjson = {
                "dataID" : resDataID, 
                "source" : image['source'], 
                "length" : image['length'], 
                "contentType" : image['contentType'], 
                "encoding" : image['encoding']
            }
            print('abc')
            data = findDataByID(resDataID)[0]
            if data['type'] != 'image': return {'error': 'Wrong Data Type!'}, 400
            res = insertImage(image)
            print('abc')
            imgID = res[0]['_id']
            data['InfoID'] = imgID
            updateData(data)
            return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@data_blueprint.post('/text')
def insertDataTextInstance():
    try:
        text = request.get_json()
        #Kiểm tra sự tồn tại của body
        if not text:
            return jsonify({"error": "Bad Request"}), 400
        
        if request.form.get('uploaderID'): text['uploaderID'] = ObjectId(request.form.get('uploaderID'))
        else:
            text['uploaderID'] = None
        if 'uploaderID' not in text:
            access_token = request.headers.get('Authorization')
            if not access_token: return jsonify({"error": "Bad Request"}), 400 
            text['uploaderID'] = checkToken(access_token)[0]

        insertDataJSON = {
            'uploaderID': text['uploaderID'],
            'type': 'text'
        }
        resData = insertData(insertDataJSON)[0]
        resDataID = resData['_id']
        #["dataID", "source", "length", "contentType", "encoding"]
        #Trường Required
        if 'content' not in text: 
            return jsonify({"error": "Missing Required Values"}), 400 
        #Đảm bảo các trường có đúng không
        for key in text.keys():
            if key not in ["uploaderID", "content"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        #Xử lý viết file vào storage
        fileName = f'text_{time.time()}.txt'
        data = findDataByID(resDataID)[0]
        if data['type'] != 'text': return {'error': 'Wrong Data Type!'}, 400
        #Đưa vào db
        inputDb = {
            "dataID" : resDataID,
            'source': fileName
        }
        res = insertText(inputDb)
        data['InfoID'] = res[0]['_id']
        updateData(data)
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
    
@data_blueprint.put('/')
def changeDataInstance():
    try:
        print('abc')
        data = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not data:
            return jsonify({"error": "Bad Request"}), 400
        
        print(len(data["_id"]))
        if len(data["_id"])!=24:
            return jsonify({"error": "Bad Request"}), 400
        
        #Đảm bảo các trường có đúng không
        for key in data.keys():
            if key not in ["segmentID","uploaderID","type","InfoID","uploadTime","processed","processed_time","TrainValTest","location","_id"]:
                return jsonify({"error": "Wrong key provided"}), 400 

        checkData = findDataByID(data['_id'])
        if data['uploaderID'] != checkData['uploaderID']: 
            return jsonify({"error": "uploaderID is different from the original one"}), 400
        res = updateData(data)
        return res         
    except Exception as e:
        print(e)
        return str(e), 500
    
@data_blueprint.delete('/<id>')
def deleteDataID(id): #Phải xóa image, video kèm theo (nếu có) và xóa luôn status của data đó
    try:
        access_token = request.headers.get('Authorization')
        res = findDataByID(id)
        if res[0]['uploaderID'] != checkToken(access_token)[0] and not checkAdmin(access_token): 
            return 'Forbidden', 403
        if res[0]['type'] == 'text':
            deleteText(res[0]['InfoID'])
        elif res[0]['type'] == 'image':
            deleteImage(res[0]['InfoID'])
        res = deleteData(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500

@data_blueprint.get('/eval/<id>')
def evaluateStatus(id):
    try:
        data = findDataByID(id)[0]
        infoID = data['InfoID']
        if data['type'] == 'image':
            img = findImageByID(infoID)[0]
            imgSrc = os.getenv('STORAGE') + '/images/unverified/' + img['source']
            print(imgSrc)
            policeEval = TestForPolices(imgSrc)
            obstaclesEval = TestForObstacles(imgSrc)
            trafficJamEval = TestForTJam(imgSrc)
            floodedEval = TestForFlooded(imgSrc)
            return ({
                "policeEval": 
                {
                    "status": policeEval[0],
                    "score": policeEval[1]
                },
                "obstaclesEval":{
                    "status": obstaclesEval[0],
                    "score": obstaclesEval[1]
                },
                "trafficJamEval": {
                    "status": trafficJamEval[0],
                    "score": trafficJamEval[1]
                },
                "floodedEval": {
                    "status": floodedEval[0],
                    "score": floodedEval[1]
                },
                "type": 'img'}, 200)
        elif data['type'] == 'text':
            data = findDataByID(id)[0]
            infoID = data['InfoID']
            policeEval = EvaluateRandomExample()
            obstaclesEval = EvaluateRandomExample()
            trafficJamEval = EvaluateRandomExample()
            floodedEval = EvaluateRandomExample()
            return ({
                "policeEval": 
                {
                    "status": policeEval[0],
                    "score": policeEval[1]
                },
                "obstaclesEval":{
                    "status": obstaclesEval[0],
                    "score": obstaclesEval[1]
                },
                "trafficJamEval": {
                    "status": trafficJamEval[0],
                    "score": trafficJamEval[1]
                },
                "floodedEval": {
                    "status": floodedEval[0],
                    "score": floodedEval[1]
                },
                "type": 'text'}, 200)
    except Exception as e:
        print(e)
        return str(e), 500
    
@data_blueprint.put('/manualVerify') #Cần thêm swagger
def toggleManualVerify():
    try:
        #Check Admin
        access_token = request.headers.get('Authorization')
        if not checkAdmin(access_token): 
            return 'Forbidden', 403
        body = request.get_json()
        data = findDataByID(body['_id'])
        data["processed"] = not data["processed"]
        res = updateData(data)
        return res
    except Exception as e:
        print(e)
        return str(e), 500

@data_blueprint.put('/trainValTest') #Cần thêm swagger
def putTrainValTestValue():
    try:
        #Check Admin
        access_token = request.headers.get('Authorization')
        if not checkAdmin(access_token): 
            return 'Forbidden', 403
        body = request.get_json()
        data = findDataByID(body['_id'])
        data["processed"] = not data["processed"]
        res = updateData(data)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@data_blueprint.get('/dataByUploader')
def getDataByUploader():
    try:
        access_token = request.headers.get('Authorization')
        uploaderID = checkToken(access_token)[0]
        data, status = findDataByUploaderID(uploaderID)
        return jsonify(convert_obj(data)), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500