from flask import Flask, jsonify,request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import numpy
import requests
import subprocess
import json

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ImgReg
users = db["Users"]



class Register(Resource):
    def post(self):
        # get the posted data
        postData = request.get_json()
        username = postData["Username"]
        password = postData["Password"]

        # check if the name is in DB
        if userExists(username):
            return jsonify({
                "status": 301,
                "msg": "The username is invalid"
            })

        # update the users
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Tokens": 5
        })
        return jsonify({
            "status": 200,
            "msg": "Signed up successfully"
        })

class Classify(Resource):
    def post(self):
        postData = request.get_json()
        username = postData["Username"]
        password = postData["Password"]
        url = postData["url"]

        # verify userinfo
        if not verifiedUser(username, password):
            return jsonify({
                "status": 301,
                "msg": "Username or password is invalid"
            })

        # check user balance
        tokens_left = users.find({
            "Username": username
        })[0]["Tokens"]

        if tokens_left <= 0:
            return jsonify({
                "status": 302,
                "msg": "Please refill tokens"
            })

        # classify
        r = requests.get(url)

        with open("temp.jpg", "wb") as img:
            img.write(r.content)
            img.close()
            process = subprocess.Popen("python ./classify_image.py --model_dir=. --image_file=./temp.jpg", shell=True)
            ret = process.communicate()[0]
            process.wait()
            with open("text.txt") as text_file:
                users.update({
                    "Username": username
                }, {
                    "$set": {
                        "Tokens": tokens_left - 1
                    }
                })
                return json.load(text_file)


class Refill(Resource):
    def post(self):
        postData = request.get_json()
        username = postData["Username"]
        password = postData["Password"]
        amount = postData["Amount"]

        if not userExists(username):
            return jsonify({
                "Status": 301,
                "msg": "invalid username"
            })
        admin_pw = "chairmanMao"
        if not password == admin_pw:
            return jsonify({
                "Status": 304,
                "msg": "incorrect admin password"
            })

        # the actual refill
        prev_amount = users.find({
            "Username": username
        })[0]["Tokens"]

        users.update({
            "Username": username
        }, {
            "$set", {
                "Tokens": prev_amount
            }
        })

        return jsonify({
            "Status": 200,
            "msg": "refill done!"
        })



# check if the username exists in the DB
def userExists(username):
    user = users.find({
        "Username": username
    })
    if user.count() == 0:
        return False
    return True

def verifiedPw(username, password):
    if not userExists(username):
        return False
    stored_pw = users.find({
        "Username": username
    })[0]["Password"]
    if bcrypt.hashpw(password.encode('utf8'), stored_pw) == stored_pw:
        return True
    return False


def verifiedUser(username, password):
    if not userExists(username):
        return False
    if not verifiedPw(username, password):
        return False
    return True



api.add_resource(Register, '/register')
api.add_resource(Classify, '/classify')
api.add_resource(Refill, '/refill')

if __name__ == "__main__":
    app.run(host='0.0.0.0')