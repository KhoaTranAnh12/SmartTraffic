from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

#Add CORS into app
CORS(app)

#Swagger Config
SWAGGER_URL = "/swagger"
API_URL = "../static/swagger.json"  # Your OpenAPI JSON file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Sample API 2"},
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

#Import other blueprints
from data.dataController import data_blueprint
app.register_blueprint(data_blueprint, url_prefix = '/data')


if __name__ == '__main__':
    app.run(debug=True)