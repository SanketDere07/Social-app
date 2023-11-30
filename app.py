from flask import Flask, render_template, request,jsonify,redirect,url_for
from pymongo import MongoClient
from datetime import datetime
import base64
import os
from torchvision.utils import save_image
from werkzeug.utils import secure_filename
from bson.binary import Binary
from io import BytesIO
import string

app = Flask("__name__")



login_data=[]

client = MongoClient("mongodb://localhost:27017")
db = client["Coffee"]
user = db["user"]
posts = db["posts"]
UPLOAD_FOLDER = 'static/uploads'
# ============================================
@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template("home.html",login_data=login_data)

@app.route("/create_post_show", methods=["POST", "GET"])
def create_post_show():
    return render_template("create_post.html",login_data=login_data)

@app.route("/login")
def login():
        return render_template("login.html")

@app.route("/profile")
def profile():
    print("===lof === ",login_data)
    return render_template("profile.html",login_data=login_data)


# ============================================

@app.route("/", methods=["POST", "GET"])
def signup_page():
    if request.method == "POST":
        data = request.get_json()
        my_val = {
            "firstname": data["firstname"],
            "lastname": data["lastname"],
            "email": data["email"],
            "password": data["password"],
            "confirm_password": data["confirm_password"],
        }
        user.insert_one(my_val)
        print(data)
    return render_template("signup.html")



@app.route("/login_page", methods=["POST", "GET"])
def login_page():
    if request.method == "POST":
        data = request.get_json()
        values = user.find_one(
            {"email": data["email"], "password": data["password"]}, {"id": 0}
        )
        if values is not None:
            print("values ===>>",values)
            data_user = {
            "firstname": values["firstname"],
            "lastname": values["lastname"],
            "status":"correct"
            }
            login_data.append(data_user)
            return jsonify("correct")
    return "incorrect"




@app.route("/create_post", methods=["POST", "GET"])
def create_post():
    if request.method == "POST":
        post_content = request.form['post']
        username = login_data[0]['firstname'] + ' ' + login_data[0]['lastname']
        photo = request.files.get('post_img')
        if photo:
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            filename = secure_filename(photo.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            photo.save(filepath)

            with open(filepath, 'rb') as file:
                rv = base64.b64encode(file.read())

            document = {
                'filename': filename,
                'content_type': photo.content_type,
                'data': rv
            }
            posts.insert_one({"posts": post_content, "username": username, "photo": document})
            return redirect(url_for('profile'))
    return "ok"

@app.route("/all_user_post", methods=["POST", "GET"])
def all_user_post():
    post_list = []
    if request.method == "POST":
        data = request.get_json()
        print("all user data --->", data)
        posts_data = posts.find({"username": data['username']}, {"_id": 0, "document": 0})

        for post in posts_data:
            if 'photo' in post and 'data' in post['photo']:
                post['photo']['data'] = post['photo']['data'].decode('utf-8')

            post_list.append(post)

        # print("all user posts:", post_list)
        return jsonify(post_list)

    return "ok"

@app.route("/get_all_users_post", methods=["POST", "GET"])
def get_all_users_post():
    post_list = []
    posts_data = posts.find({}, {"_id": 0, "document": 0})
    for post in posts_data:
        if 'photo' in post and 'data' in post['photo']:
            post['photo']['data'] = post['photo']['data'].decode('utf-8')
        post_list.append(post)
    return jsonify(post_list)


if __name__ == "__main__":
    app.run(debug=True)
