from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

#Add CORS into app
CORS(app)

#Swagger Config
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"  # Your OpenAPI JSON file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Sample API 2"},
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static',path)



@app.get('/info/{id}')
def getInfo(id):
    return{
        "dataID": 1,
        "velocity": 5,
        "status": "traffic jam"
    }

@app.get('/user/{id}')
def getUser(id):
    return {
        "userID": 1,
        "fullName": "chen aang khoai",
        "DoB": "27/03/2003",
        "phoneNum": "0777111234",
        "email": "abc@gmail.com",
        "status": "ok",
        "username": "khoachenaang@gmail.con",
        "password": "123456"
    }

@app.get('/segment/{id}')
def getSegment(id):
    return {
        "ID": 1,
        "startNode": 1,
        "endNode": 2,
        "coordinations": {
            "start": (1,2),
            "end": (3,4)
        },
        "name": "abc",
        "length": 12
    }

@app.get('/nodeOSM/{id}')
def getNodeOSM(id):
    return {
        "ID": 1,
        "coordination": (1,2),
        "wayOSMID": 1,
        "segmentID": 1
    }

@app.get('/wayOSM/{id}')
def getWayOSM(id):
    return {
        "ID": 1,
        "tags": {
            "maxVelo": 1,
            "abc": 123
        },
        "coordinations": {
            "start": (1,2),
            "end": (3,4)
        },
    }



if __name__ == "__main__":
    app.run(debug=True)