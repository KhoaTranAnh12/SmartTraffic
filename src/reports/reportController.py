from flask import Blueprint

report_blueprint = Blueprint('report',__name__)

@report_blueprint.get('/{id}')
def getReport(id):
    return {
        "ID": 1,
        "textID": 1,
        "videoID": 1,
        "imageID": 1,
        "score": 0.75
    }