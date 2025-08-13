from flask import Blueprint, request, jsonify
from Z_Services.ReportServices import *
from Z_Services.UserServices import checkAdmin, checkToken
from Z_Services.DataServices import deleteData,findDataByID
from Z_Controller.DataController import evaluateStatus
from pymongo.errors import PyMongoError
report_blueprint = Blueprint('report',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@report_blueprint.before_request
def reportBeforeRequest():
    #Check Access Token
    access_token = request.headers.get('Authorization')
    if not access_token:
        return 'No access token in header', 401
    try:
        checkToken(access_token)
    except Exception as e:
        print(e)
        return str(e), 401
    
# "TrafficStatusID", "velocity"
@report_blueprint.get('/')
def getAllReport():
    try:
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token):
            res = findAllReport()
            return res
        else:
            return 'Forbidden', 403 
    except Exception as e:
        print(e)
        return str(e), 500
    
@report_blueprint.get('/notQualified')
def getAllUnqualifiedReport():
    try:
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token):
            res = findAllUnqualifiedReport()
            return res
        else:
            return 'Forbidden', 403 
    except Exception as e:
        print(e)
        return str(e), 500

@report_blueprint.get('/<id>')
def getReportID(id):
    try:
        #Tìm uploader:
        res = findReportByID(id)
        uploader = res[0]['uploaderID']
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == uploader:
            return res
    except Exception as e:
        print(e)
        return str(e), 500
    

@report_blueprint.get('/uploader/<id>') #New, chưa thêm swagger
def getReportByUploaderID(id):
    try:
        #Check Token xem có đúng uploader hay admin hay không
        access_token = request.headers.get('Authorization')
        if checkAdmin(access_token) or checkToken(access_token)[0] == id:
            res = findReportByUploaderID(id)
            return res
        else:
            return 'Forbidden', 403
    except Exception as e:
        print(e)
        return str(e), 500


# "uploaderID": {"bsonType": "objectId"},
# "textID": {"bsonType": "objectId"},
# "imageID": {"bsonType": "objectId"},
# "eval": {"bsonType": "float"},
# "qualified": {"bsonType": "bool"},
# "createdDate": {"bsonType": "date"}
@report_blueprint.post('/')
def insertReportInstance():
    try:
        # ["uploaderID", "textID", "imageID", "eval", "qualified", "createdDate"]
        report = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not report:
            return jsonify({"error": "Bad Request"}), 400
        
        #Trường Required
        if 'uploaderID' not in report:   
            return jsonify({"error": "Missing Required Values"}), 400 
        
        if len(report["uploaderID"])!=24:
            return jsonify({"error": "Bad Request"}), 400

        #Đảm bảo các trường có đúng không
        for key in report.keys():
            if key not in ["uploaderID", "textID", "imageID", "eval", "qualified", "createdDate"]:
                return jsonify({"error": "Wrong key provided"}), 400 
        
        res = insertReport(report)
        return res
    except Exception as e:
        print(e)
        return str(e), 500

@report_blueprint.put('/')
def changeReportInstance():
    try:
        print('abc')
        report = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not report:
            return jsonify({"error": "Bad Request"}), 400
        
        if len(report["uploaderID"])!=24:
            return jsonify({"error": "Bad Request"}), 400

        #Đảm bảo các trường có đúng không
        for key in report.keys():
            if key not in ["uploaderID", "textID", "imageID", "eval", "qualified"]:
                return jsonify({"error": "Wrong key provided"}), 400

        checkReport = findReportByID(report['_id'])
        if report['uploaderID'] != checkReport['uploaderID']: 
            return jsonify({"error": "uploaderID is different from the original one"}), 400
        res = updateReport(report)
        return res         
    except Exception as e:
        print(e)
        return str(e), 500
    
@report_blueprint.delete('/<id>')
def deleteReportID(id): #Phải xóa image, video kèm theo (nếu có) và xóa luôn status của report đó
    try:
        access_token = request.headers.get('Authorization')
        res = findReportByID(id)
        if res[0]['uploaderID'] != checkToken(access_token)[0] and not checkAdmin(access_token): 
            return 'Forbidden', 403
        if res[0]['textID']:
            deleteData(res[0]['textID'])
        elif res[0]['imageID']:
            deleteData(res[0]['imageID'])
        res = deleteReport(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@report_blueprint.put('/autoVerify') #Cần thêm swagger
def autoVerifybyID(id):
    try:
        report = findReportByID(id)
        #Tìm textID và ImgID để tính toán
        currTextID = report['dataTextID']
        currImgID = report['dataImgID']
        #Lấy Img và Text để chấm
        text = evaluateStatus(currTextID)[0]
        img = evaluateStatus(currImgID)[0]
        #Dùng harmony để tính:
        harmony = {}
        for k in text.keys():
            if text[k]['status']==img[k]['status']:
                harmony[k] = {
                    "status": text[k]['status'],
                    "score": (text[k]['score']*img[k]['score']*2)/(text[k]['score']+img[k]['score'])
                }
            else:
                if text[k]['status'] == False:
                    harmony[k] = {
                        "status": False,
                        "score": (text[k]['score']*(1-img[k]['score'])*2)/(text[k]['score']+(1-img[k]['score']))
                    }
                else:
                    harmony[k] = {
                        "status": False,
                        "score": ((1-text[k]['score'])*img[k]['score']*2)/((1-text[k]['score'])+img[k]['score'])
                    }

    except Exception as e:
        print(e)
        return str(e), 500