from flask import Blueprint

dataInfo_blueprint = Blueprint('dataInfo',__name__)

@dataInfo_blueprint.get('/{id}')
def getDataInfo(id):
    return {
        "dataID": 1,
        "dataType": "image",
        "ID": 1,
        "verified": False,
        "verifiedDate": None,
        "verifiedUntil": None,
        "train/val/test": "train",
        "encoding": "base64",
        "format": "png",
        "content": "2as25d5sd3a3asd2asc2as", 
    }