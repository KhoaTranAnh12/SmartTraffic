from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from Z_Controller.DataController import data_blueprint
from Z_Controller.UserController import user_blueprint
from Z_Controller.NotificationController import notifications_blueprint
from Z_Controller.ImageController import image_blueprint
from Z_Controller.AuthController import auth_blueprint
# from Z_Controller.TrafficStatusController import trafficStatus_blueprint
from Z_Controller.TrafficStatusInfoController import trafficStatusInfo_blueprint
from Z_Controller.NodeOSMController import nodeOSM_blueprint
from Z_Controller.WayOSMController import wayOSM_blueprint
from Z_Controller.RelationOSMController import relationOSM_blueprint
from Z_Controller.SegmentController import segment_blueprint
from Z_Controller.TextController import text_blueprint
from EvaluationLib.main import *
from datetime import datetime, timedelta
from flask_jwt_extended import (
    JWTManager
)
import os
from dotenv import load_dotenv

app = Flask(__name__)

#Add CORS into app
CORS(app)

#Config JWT
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET')  # Thay bằng khóa bí mật mạnh
app.config['JWT_SECRET_KEY'] = os.getenv('JWTSECRET')  # Khóa riêng cho JWT
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

jwt = JWTManager(app)                           

#Swagger Config
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"  # Your OpenAPI JSON file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Sample API 2"},
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

#Get Controllers
app.register_blueprint(data_blueprint,url_prefix='/data')
app.register_blueprint(user_blueprint,url_prefix='/user')
app.register_blueprint(notifications_blueprint,url_prefix='/notifications')
app.register_blueprint(text_blueprint,url_prefix='/text')
app.register_blueprint(image_blueprint,url_prefix='/image')
app.register_blueprint(auth_blueprint,url_prefix='/auth')
# app.register_blueprint(trafficStatus_blueprint,url_prefix='/trafficStatus')
app.register_blueprint(trafficStatusInfo_blueprint,url_prefix='/trafficStatusInfo')
app.register_blueprint(nodeOSM_blueprint,url_prefix='/nodeOSM')
app.register_blueprint(wayOSM_blueprint,url_prefix='/wayOSM')
app.register_blueprint(relationOSM_blueprint,url_prefix='/relationOSM')
app.register_blueprint(segment_blueprint,url_prefix='/segment')


if __name__ == "__main__":
    app.run(debug=True)