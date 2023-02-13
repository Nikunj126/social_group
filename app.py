from flask import Flask
from Database.db import initialize_db
from flask_restful import Api
from Routes.routes import *
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt


app = Flask(__name__)
api = Api(app)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost:27017/social_group'
}

app.config['JWT_SECRET_KEY'] = 't1NP63m4wnBg6nyHYKmc2TpCORGI4nss'

bcrypt = Bcrypt(app)
jwt = JWTManager(app)


initialize_db(app)
initialize_routes(api)

if __name__ == '__main__':
    app.run(debug=True)
