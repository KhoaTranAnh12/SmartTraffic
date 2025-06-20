from flask import Blueprint

data_blueprint = Blueprint('data',__name__)

@data_blueprint.get('/{id}')
def getData(id):
    return {
        "ID": id,
        "segmentID": 1,
        "uploaderID": 1,
        "type": "video",
        "infoID": 1,
        "dataInfoID": 1,
        "uploadDate": '2025/09/15'
    }