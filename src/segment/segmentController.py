from flask import Blueprint

segment_blueprint = Blueprint('segment',__name__)

@segment_blueprint.get('/{id}')
def getSegment(id):
    return {
        "ID": id,
        "startNode": 1,
        "endNode": 2,
        "coordinations": {
            "start": (1,2),
            "end": (3,4)
        },
        "name": "abc",
        "length": 12
    }



