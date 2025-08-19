from Z_DBAccessLayer.DBConnect import TrafficMongoClient
from Z_Services.NodeOSMServices import findNodeOSMInSegmentbyCoor
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from flask import jsonify
client = TrafficMongoClient()


#Toàn bộ giá trị trả về trong phần Try đều phải trả về bằng tuple (res, statusCode)
#Toàn bộ dữ liệu không phải string thì update lại


segmentTable = client.db["segments"]
#["type","id","way_id","segments","tags","version","timestamp","changeset","uid","user"]:
def findAllSegment():
    try:
        res = segmentTable.find()
        res = list(res)
        return res, 200
    except PyMongoError as e:
        raise e


def findSegmentByID(id):
    try:
        res = segmentTable.find_one({"id": id})
        if res == None: return {}, 200
        return res, 200
    except PyMongoError as e:
        raise e
    
def findSegmentByCoor(lat,lon):
    try:
        res = findNodeOSMInSegmentbyCoor(lat,lon)[0]
        if res == {}: return {}, 200
        nodeID = res['id']
        res = segmentTable.find({"nodes": nodeID})
        if res == None: return {}, 200
        return list(res), 200
    except PyMongoError as e:
        raise e    

def updateSegment(body):
    try:
        res = segmentTable.find_one({"id": body['id']})
        if res == None: 
            return jsonify({"error": "Not Found"}), 404
        segmentTable.update_one({'id': body['id']}, {"$set": body})
        return body, 201
    except PyMongoError as e:
        raise e


def findSegmentsInBoundingBox(corner1, corner2):
    try:
        lat_min = min(corner1[0], corner2[0])
        lat_max = max(corner1[0], corner2[0])
        lon_min = min(corner1[1], corner2[1])
        lon_max = max(corner1[1], corner2[1])
        res_cursor = segmentTable.find({
            "$or": [
                {
                    "$and": [
                        {"polyline.coordinates.0.1": {"$gte": lat_min, "$lte": lat_max}},
                        {"polyline.coordinates.0.0": {"$gte": lon_min, "$lte": lon_max}},
                    ]
                },
                {
                    "$and": [
                        {"polyline.coordinates.1.1": {"$gte": lat_min, "$lte": lat_max}},
                        {"polyline.coordinates.1.0": {"$gte": lon_min, "$lte": lon_max}},
                    ]
                }
            ]
        })

        results = []
        for doc in res_cursor:
            doc.pop('_id', None)
            results.append(doc)

        return results, 200

    except PyMongoError as e:
        raise e