from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
import datetime
from OPS.auth import *


class SignUp(Resource):
    @staticmethod
    def post():
        try:
            body = request.get_json()
            user = user_db(**body)
            user.hash_password()
            user.save()
            _id = user.id
            return {'id': str(_id)}, 200
        except NotUniqueError:
            return "User name is already taken, please try other user name."


class LogIn(Resource):
    @staticmethod
    def post():
            body = request.get_json()
            user_name = body["user_name"]
            if is_user(user_name):
                user = user_db.objects.get(user_name=user_name)
                authorized = user.check_password(body.get("password"))
                if not authorized:
                    return "Username or password invalid!!"
                else:
                    expires = timedelta(days=7)
                    access_token = create_access_token(identity=str(user.id), expires_delta=expires)
                    return {'token': access_token}, 200
            else:
                return "{} : User not found!!".format(user_name)
