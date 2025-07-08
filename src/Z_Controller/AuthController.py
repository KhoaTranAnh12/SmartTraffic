from flask import Blueprint, request, jsonify
from Z_Services.UserServices import *
from pymongo.errors import PyMongoError
auth_blueprint = Blueprint('auth',__name__)


@auth_blueprint.post('/login')
def userLogin():
    try:
        user = request.get_json()
        if 'username' not in user or 'password' not in user: 
            return jsonify({"error": "Missing Required Values"}), 400 
        for key in user.keys():
            if key not in ["username" , "password"]:
                return jsonify({"error": "Wrong key provided"}), 400
        res = login(user)
        return res
    except Exception as e:
        print(e)
        return str(e), 500
    
@auth_blueprint.post('/refresh')
def refreshTokenAuth():
    try:
        body = request.get_json()
        if 'token' not in body or 'username' not in body: 
            return jsonify({"error": "Missing Required Values"}), 400 
        for key in body.keys():
            if key not in ["username" , "token"]:
                return jsonify({"error": "Wrong key provided"}), 400
        res = refreshToken(body)
        return res
    except Exception as e:
        print(e)
        return str(e), 500