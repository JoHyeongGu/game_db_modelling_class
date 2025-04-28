import os
from flask import Flask, jsonify, session, url_for, request, redirect, render_template_string
from flask import render_template

app = Flask(__name__)
app.secret_key = "game_database_modeling_class"

user_data = {
    "admin" : {
        "id" : 1,
        "name" : "HyeongGu Jo",
        "nickname" : "JHG",
        "password" : "1234",
        "email" : "ddd@gmail.com",
    },
}

#region 로그인 흉내내기
@app.route("/")
def main():
    if session.get("login") in user_data.keys():
        return render_template("login.html")
    else:
        return render_template("fetch_test.html")

@app.route("/login", methods=["GET"])
def login():
    if session.get("login") != None:
        return jsonify({"state": 200, "message": "Already Logged In", "username": session["login"]})
    username = request.form.get("username")
    password = request.form.get("password")
    if username in user_data.keys() and password == user_data[username]["password"]:
        session["login"] = username
        return jsonify({"state": 200, "username": username, "password": password})
    else:
        return jsonify({"state": 403, "error": "Incorrect UserName or Password", "username": username})
    
@app.route("/logout")
def logout():
    session.pop("login", None)
    return jsonify({"state": 200, "message": "Logout Complete"})
#endregion 로그인 흉내내기

#region 유저 정보 REST
@app.route("/user/<string:username>", methods=["GET"])
def get_user(username):
    if username == None or username == "" or username == "all":
        return jsonify(user_data)
    elif username not in user_data.keys():
        return jsonify({"state": 403, "message": "user can't be found."})
    else:
        data = user_data[username].copy()
        data["id"] = username
        return jsonify(data)

@app.route("/user/register", methods=["POST"])
def create_user():
    data = request.get_json()
    if "username" not in data.keys() or "password" not in data.keys():
        return jsonify({"state": 400, "message": "username, password are essential."})
    username = data["username"]
    if username in user_data.keys():
        return jsonify({"state": 400, "message": username+" is already registered."})
    del data["username"]
    user_data[username] = data
    return jsonify({"state": 200, "username": username})

@app.route("/user/delete", methods=["DELETE"])
def delete_user():
    data = request.get_json()
    if "username" not in data.keys() or "password" not in data.keys():
        return jsonify({"state": 400, "message": "username, password are essential."})
    username = session["username"] if session.get("username") != None else data["username"]
    password = session["password"] if session.get("password") != None else data["password"]
    if username not in user_data.keys():
        return jsonify({"state": 403, "message": "User can't be found."})
    elif password == user_data[username]["password"]:
        del user_data[username]
        return jsonify({"state": 200, "username": username, "message": "Delete Complete"})
    else:
        return jsonify({"state": 400, "message": "You can't delete account."})
    
@app.route("/user/update/<string:username>", methods=["PATCH"])
def update_user(username):
    if username not in user_data.keys():
        return jsonify({"state": 403, "message": "User can't be found."})
    data = request.get_json()
    if "username" in data.keys():
        if len(data.keys()) == 1:
            ori_data = user_data[username]
            user_data[data["username"]] = ori_data
            del user_data[username]
        else:
            ori_data = user_data[username]
            new_username = data["username"]
            del data["username"]
            for k, v in data.items():
                if v == None:
                    del ori_data[k]
                else:
                    ori_data[k] = v
            del user_data[username]
            user_data[new_username] = ori_data
    else:
        ori_data = user_data[username]
        for k, v in data.items():
            if v == None:
                del ori_data[k]
            else:
                ori_data[k] = v
        user_data[username] = ori_data
    return jsonify({"state": 200, "username": username, "message": "Update Complete"})
#endregion 유저 정보 REST

#region 기본 API 요청 구성
@app.route("/hello/<int:id>", methods=["GET"])
def hello_world(id):
    data = {
        1: {
            "id": 0,
            "name" : "JHG",
            "email": "ddd@gmail.com",
            "is_active": True,
        },
        2: {
            "id": 1,
            "name" : "SBJ",
            "email": "ssss@gmail.com",
            "is_active": False,
        },
    }
    user = data.get(id, None)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User Id is not found", "user_id": id, "name": id})
#endregion 기본 API 요청 구성
  
#region 팔로우 메세지 구조 설계
"""_summary_
userDB = [
    { 
        "id" : 1, "username": "bseo"
    },
    {
        "id" : 2, "username": "beomjoo90", 
    }
]

messageDB = [
    { "id" : 1, "content": "this is the first beomjoo X message.", "from": "bseo", "to" : null, "reply_from": null},
    { "id" : 2, "content": "welcome beomjoo90. this is your first reply message.", "from": "beomjoo90", "to" : "bseo", "reply_from": 1},
]

followers = [
    { "id": 1, "username": "bseo", "folllowing": "beomjoo90" },
    { "id": 2, "username": "beomjoo90", "folllowing": "test" },
    { "id": 3, "username": "bseo", "folllowing": "test" },
]

0. user management

    GET /user/all -- list registered users
    GET /user/[username] -- list a specific user's info (with username)
    POST /user/register -- create a new user using body json request
    PATCH /user/update/[username] -- Update specific user's information with username & body json
    DELETE /user/delete -- delete a specific user with body json (judge the authority with password & id)
    

1. follow (allowed for a logged user)

    0. assume a logged user is "bseo". all registered users are "test", "bseo", "beomjoo90"

    GET /followers  -- list my following users
        req: none
        res: application/json
            {"followers": [ ]} if no following users
            {"followers": [ "beomjoo90" ]} array contains following users' username of a given user    
    POST /followers  -- create a new follower from my following list
        req: application/json
            { "username": "beomjoo90" }
        res: application/json
            {"followers": [ "beomjoo90"] }
    GET /followers/[username] -- list followers of a specified user (e.g. beomjoo90)
        restriction: list followers of the given "following" user
        req: none
        res: application/json
            {"followers: [ "test" ]} if bseo follows beomjoo90
            {"followers: [], "error msg" : "un-authorized user's request" }    
    DELETE /followers/[username] -- remove beomjoo90 from my following list 
        res: application/json
            {"followers: [] } -- show the list of the logged user's followers    

2. message

    GET /messages -- Get all Messages
        res: application/json
            [{ "id" : 1, "content": "Message content", "from": "jhg", "to" : [username], "reply_from": null}]
    GET /messages/[username] -- Get all Messages from specific user
    GET /message/recieve/[username] -- Get all Messages that specific user took
        res: application/json
            { "id" : 1, "content": "Message content", "from": "jhg", "to" : [username], "reply_from": null}
    POST /messages/send/[username] -- Create New Message
        req: application/json
            { "content": "Message content", "to": "jhg" }
        res: application/json
            { "id" : 1, "content": "Message content", "from": [username], "to" : "jhg", "reply_from": null}
    DELETE /messages/[id] -- Delete Specific Message
        res: application/json
            { "id" : [id], "content": "Message content", "from": [username], "to" : "jhg", "reply_from": null}
"""
#endregion 팔로우 메세지 구조 설계  

#region Sample Data for Follow&Message
user_db = [
    {"id": 1, "username": "jhg", "email": "test"},
    {"id": 2, "username": "bseo", "email": "test"},
    {"id": 3, "username": "test", "email": "test"},           
]

follow_db = [
    {"id" : 1, "username" : "jhg", "follower" : "bseo"},
    {"id" : 2, "username" : "bseo", "follower" : "jhg"},
]

message_db = [ ]
#endregion

#region 팔로우 기능
@app.route("/follows", methods=["GET"])
def list_following():
    username = session.get("login", None)
    followers = next((data["follower"] for data in follow_db if data["username"] == username), [])
    return jsonify({"followers" : followers})

@app.route("/follows", methods=["POST"])
def create_follower():
    username = session.get("login", None)
    data = request.get_json()
    if username == None or not data or not "username" in data:
        return jsonify({"followers": []})
    new_follower = data.get("username")
    followers = next((data["follower"] for data in follow_db if data["username"] == username), None)
    follower = next((follower for follower in followers if follower == new_follower), None)
    if follower != None:
        return jsonify({"followers": followers})
    follower_db.append({"id" : len(follower_db), "username" : username, "follower" : new_follower})
    followers = next((data["follower"] for data in follow_db if data["username"] == username), None)
    return jsonify({"followers" : followers})
#endregion 팔로우 기능

#region 메세지 기능
@app.route("/messages", methods=["GET"])
def list_messages():
    messages = [m for m in message_db if m["from"] == logged_user or m["to"] == logged_user]
    return jsonify({"messages": messages})


@app.route("/messages", methods=["POST"])
def send_message():
    data = request.get_json()
    recipient = data.get("to")
    content = data.get("content")

    if recipient not in users or recipient == logged_user:
        return abort(400, "Invalid recipient")

    new_message = {
        "id": len(message_db) + 1,
        "content": content,
        "from": logged_user,
        "to": recipient,
        "reply_from": None
    }
    message_db.append(new_message)
    return jsonify(new_message), 201


@app.route("/messages/<int:message_id>/reply", methods=["POST"])
def reply_message(message_id):
    original = next((m for m in message_db if m["id"] == message_id), None)
    if not original:
        return abort(404, "Original message not found")

    data = request.get_json()
    content = data.get("content")

    new_message = {
        "id": len(message_db) + 1,
        "content": content,
        "from": logged_user,
        "to": None,
        "reply_from": message_id
    }
    message_db.append(new_message)
    return jsonify(new_message), 201
#endregion 메세지 기능

if __name__ == "__main__":
    app.run(debug=True)