from flask_restful import reqparse, Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from passlib.hash import sha256_crypt
from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import requests
import json
import jwt

app = Flask(__name__)
app.secret_key = "secrectkey"
app.permanent_session_lifetime = datetime.timedelta(minutes=45)
api = Api(app)
CORS(app)

market_url  = 'https://api.bittrex.com/v3/markets'
users= [
    {
        'username' : 'user1',
        'password' :  sha256_crypt.hash('user1')
    },
    {
      'username' : 'user2',
        'password' :  sha256_crypt.hash('user2')
    }]


def validate_jwt(token):
    try:
        data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        print(data)
    except jwt.ExpiredSignatureError:
        print("Token Expired! please re-login to continue")
        return False
    except Exception as err:
        print("Token error", err)
        return False
    return True


def is_logged_in(f):
    def wrap(*args, **kwargs):
        if "Authorization" in request.headers and validate_jwt(request.headers["Authorization"]):
            return f(*args, **kwargs)
        else:
            return {"msg": "Unauthorized, Please login", "err": True}, 401
    return wrap

class Users(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, help='Enter username', required=True, location = 'json')
        self.parser.add_argument('password', type=str, help='Enter password', required=True, location = 'json')

    def post(self):
        args = self.parser.parse_args()
        print(args)
        if request.method == "POST":
            username = args["username"]
            password_candidate = args["password"]
            res = list(filter(lambda x: x["username"] == username, users))
            if res:
                result = res[0]
                password = result["password"]
                if sha256_crypt.verify(password_candidate, password):
                    token = jwt.encode({
                            "username": result["username"],
                            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=45),
                        }, app.secret_key, algorithm="HS256")
                    return {"msg": "Logged in successfully.", "token": token}
                else:
                    return {"msg": "Invalid username or password.", "err": True}, 401
            else:
                return {"msg": "User not found", "err": True}, 401

class Market(Resource):
    decorators = [is_logged_in]
    def get(self):
        summery_url = f'{market_url}/summaries'
        res = requests.get(summery_url)
        return json.loads(res.text)
        

class Summery(Resource):
    decorators = [is_logged_in]
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('market', type=str, help='Enter valid market symbol', required=True, location = 'args')
        
    def get(self):
        args = self.parser.parse_args()
        symbol = args['market']
        summery_url = f'{market_url}/{symbol}/summary'
        print(summery_url)   
        res = requests.get(summery_url)
        return json.loads(res.text)
    

# Routes
api.add_resource(Users, "/api/get_token")
api.add_resource(Market, "/api/get_all_summaries")
api.add_resource(Summery, "/api/get_summary")


# Swagger UI
SWAGGER_URL = '/swagger'
API_URL = 'http://127.0.0.1:5000/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Crypto Market API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))

if __name__ == "__main__":
    print("server init")
    app.run(host='0.0.0.0', debug=True)