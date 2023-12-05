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
likes = db["likes"]
comment = db["comment"]
follows = db["follows"]
followers = db["followers"]

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

@app.route("/follow")
def follow():
    return render_template("follow.html")
    
@app.route("/followers")
def followers():
    return render_template("followers.html")

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
            "user_uid":"1234"
        }
        id_data = user.insert_one(my_val)
        user.update_one({"_id": id_data.inserted_id}, {"$set": {"user_uid": str(id_data.inserted_id)}})
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
        username = login_data[-1]['firstname'] + ' ' + login_data[-1]['lastname']
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
            id_data = posts.insert_one({"posts": post_content, "username": username,"post_uid":"123", "photo": document})
            posts.update_one({"_id": id_data.inserted_id}, {"$set": {"post_uid": str(id_data.inserted_id)}})
            return redirect(url_for('profile'))
    return "ok"

@app.route("/all_user_post", methods=["POST", "GET"])
def all_user_post():
    if request.method == "POST":
        data = request.get_json()
        print("all user data --->", data)
        posts_data = posts.find({"username": data['username']}, {"_id": 0, "document": 0})
        post_list = []
        for post in posts_data:
            if 'photo' in post and 'data' in post['photo']:
                post['photo']['data'] = post['photo']['data'].decode('utf-8')

            post_list.append(post)
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

@app.route("/get_profile_update_data", methods=["POST", "GET"])
def get_profile_update_data():
    if request.method == "POST":
        data = request.get_json()
        username = data['username'].split()
        firstname = username[0]
        lastname = username[1]
        print("=====",firstname,lastname,"======")
        profile_data = user.find_one({"firstname": firstname,"lastname":lastname},{"_id":0})
        return jsonify(profile_data)

@app.route("/save_profile_user", methods=["POST", "GET"])
def save_profile_user():
    if request.method == "POST":
        data = request.get_json()
        user.update_one({"firstname": data['firstname'],"lastname":data['lastname']},{"$set":{"email":data['email']}})
        return "Success Update"

@app.route("/delete_profile_user", methods=["POST", "GET"])
def delete_profile_user():
    if request.method == "POST":
        data = request.get_json()
        username = data['username'].split()
        firstname = username[0]
        lastname = username[1]
        user.delete_one({"firstname": firstname, "lastname": lastname})
        return "Delete success"  

@app.route("/comment_post_data_get", methods=["POST", "GET"])
def comment_post_data_get():
    if request.method == "POST":
        data = request.get_json()
        print("post for get data of comment post -->>", data)
        post_uid = data['post_uid']

        comment_data = comment.find({"post_uid": post_uid}, {"_id": 0})
        all_comments = []

        for comment_item in comment_data:
            print("= IF part ---->>>>", comment_item)
            all_comments.append(comment_item)

        if all_comments:
            return jsonify(all_comments)
        else:
            data = {"post_uid": post_uid}
            return jsonify(data)

@app.route("/save_comment_post", methods=["POST", "GET"])
def save_comment_post():
    if request.method == "POST":
        data = request.get_json()
        print(" save comment POST data -->>",data)
        comment.insert_one({"post_uid": data["post_uid"], "comment":data['comment'],"username":data["username"]})
        return "Comment successfully Done"  
     
@app.route("/get_follow_data")
def get_follow_data():
    username = login_data[-1]['firstname'] + ' ' + login_data[-1]['lastname']
    follow_data = follows.find({"follower":username},{"_id": 0})
    if follow_data is not None:
        follow_list = []
        for item in follow_data:
            follow_list.append(item)
        print("follow_list ---->",follow_list)
        return jsonify(follow_list)
    else:
        return "No Data Found!"
    
@app.route('/follow_user',methods=["POST","GET"])
def follow_user():
    if request.method=="POST":
        data = request.get_json()
        print("add to follow data -->>",data)
        result = follows.insert_one({'follow' : data['follow'],"follower":data['follower'],"follow_uid":"1234"})
        follows.update_one({"_id": result.inserted_id}, {"$set": {"follow_uid": str(result.inserted_id)}})
        if result:
            return jsonify('User added')
        else:
            return jsonify('Failed to add user')

@app.route("/all_users_to_follow")
def all_users_to_follow():
    username = login_data[-1]['firstname'] + ' ' + login_data[-1]['lastname']
    data = user.find({"username": { "$ne": username } }, { "_id": 0 });
    follow_data = follows.find({"follower":username},{"_id":0})
    follow_suggestion_list = []
    follow_already_data =[]
    if data is not None:
        for item in data:
            username = item['firstname'] + ' ' + item['lastname']
            follow_suggestion_list.append(username)
        print("follow_list ---->",follow_suggestion_list)
    if follow_data is not None:
        for item in follow_data:
            follow_already_data.append(item['follow'])
        print("Already follow_list ---->",follow_already_data)
    suggested_users = [name for name in follow_suggestion_list if name not in follow_already_data]
    print("Suggested Users ---->", suggested_users)
    return jsonify(suggested_users)


@app.route("/get_followers_data")
def get_followers_data():
    username = login_data[-1]['firstname'] + ' ' + login_data[-1]['lastname']
    follower_data = follows.find({"follow":username},{"_id": 0})
    if follower_data is not None:
        follower_data_list = []
        for item in follower_data:
            follower_data_list.append(item)
        print("follow_list ---->",follower_data_list)
        return jsonify(follower_data_list)
    else:
        return "No Data Found!"


@app.route("/like_post" ,methods=["POST","GET"])
def like_post():
    if request.method=="POST":
        data = request.get_json()
        print("======================  LIKE DATA ====================")
        print(data)
        print("======================================================")
        result = likes.insert_one({'like_by' : data['like_by'],"post_uid":data['post_uid']})
        if result:
            return jsonify('User like added')
        else:
            return jsonify('Failed to add Like user')

@app.route("/get_like_post_data")
def get_like_post_data():
    likes_data = likes.find({},{"_id": 0})
    if likes_data is not None:
        likes_data_list = []
        for item in likes_data:
            likes_data_list.append(item)
        print("likes_data list ---->",likes_data_list)
        return jsonify(likes_data_list)
    else:
        return "No Data Found!"

if __name__ == "__main__":
    app.run(debug=True)
