from flask import Flask, jsonify, request, session
from passlib.hash import sha256_crypt
from flask_cors import CORS
import datetime
import jwt
import json

app = Flask(__name__)
app.secret_key = "secrectkey"
app.permanent_session_lifetime = datetime.timedelta(minutes=45)
CORS(app)

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
    except Exception as err:
        print("Token error", err)
        return False
    return True


def is_logged_in(f):
    def wrap(*args, **kwargs):
        if "Authorization" in request.headers and validate_jwt(request.headers["Authorization"]):
            return f(*args, **kwargs)
        else:
            return jsonify({"msg": "Unauthorized, Please login", "err": True})
    return wrap


@app.route("/api/get_token", methods=["POST"])
def login():
    print("request", request.method)
    if request.method == "POST":
        username = request.json["username"]
        password_candidate = request.json["password"]
        res = list(filter(lambda x: x["username"] == username, users))
        print(res)
        if res:
            result = res[0]
            password = result["password"]
            if sha256_crypt.verify(password_candidate, password):
                token = jwt.encode(
                    {
                        "username": result["username"],
                        "exp": datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=45),
                    },
                    app.secret_key,
                    algorithm="HS256",
                )
                return jsonify({"msg": "Logged in successfully.", "token": token})
            else:
                return jsonify({"msg": "Invalid username or password.", "err": True})
        else:
            return jsonify({"msg": "User not found", "err": True})

if __name__ == "__main__":
    print("server init")
    app.run(debug=True)