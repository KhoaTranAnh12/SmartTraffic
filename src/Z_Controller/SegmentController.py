from flask import Blueprint, request, jsonify
from Z_Services.SegmentServices import *
from pymongo.errors import PyMongoError
segment_blueprint = Blueprint('segment',__name__)

#Res gọi bằng Service đều trả không cần tuple, nếu phát sinh lỗi thì trả tuple hết.

@segment_blueprint.before_request
def segmentBeforeRequest():
    print("before segment")

@segment_blueprint.get('/')
def getAllSegment():
    try:
        res = findAllSegment()
        return res
    except Exception as e:
        print(e)
        return str(e), 500
@segment_blueprint.get('/<id>')
def getSegmentID(id):
    try:
        res = findSegmentByID(id)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
@segment_blueprint.post('/gps')
def findSegmentUsingCoor():
    try:
        coor = request.get_json()
        
    except Exception as e:
        print(e)
        return str(e), 500

@segment_blueprint.put('/')
def changeSegmentInstance():
    try:
        print('abc')
        segment = request.get_json()

        #Kiểm tra sự tồn tại của body
        if not segment:
            return jsonify({"error": "Bad Request"}), 400
        
        #Đảm bảo các trường có đúng không
        for key in segment.keys():
            if key not in ["type","id","way_id","nodes","tags","version","timestamp","changeset","uid","user"]:
                return jsonify({"error": "Wrong key provided"}), 400 

        res = updateSegment(segment)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@segment_blueprint.get("/bounding-box")
def getSegmentsInBoundingBox():
    try:
        lat1 = float(request.args.get("lat1"))
        lon1 = float(request.args.get("lon1"))
        lat2 = float(request.args.get("lat2"))
        lon2 = float(request.args.get("lon2"))

        corner1 = [lat1, lon1]
        corner2 = [lat2, lon2]

        res, status_code = findSegmentsInBoundingBox(corner1, corner2)
        return jsonify(res), status_code

    except Exception as e:
        print(e)
        return str(e), 500