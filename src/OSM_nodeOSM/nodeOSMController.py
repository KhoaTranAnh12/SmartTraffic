from flask import Blueprint

status_blueprint = Blueprint('info',__name__)

@status_blueprint.get('/{id}')
def getStatus(id):
    return {
        "ID": 1,
        "status": {
            "Construction": False,
            "TrafficJam": True,
            "Police": True,
            "Flooded": False
        },
        "velocity": 20
    }