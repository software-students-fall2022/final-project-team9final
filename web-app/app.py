from flask import Flask, jsonify, render_template, request, redirect, abort, url_for, make_response, flash, session
import os
from os import urandom
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
import sys
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import certifi
import re
from database import Database
import flask_login
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import random
import json
import openai
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = urandom(32)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


Database.initialize(os.getenv('MONGO_URI'), os.getenv('MONGO_DBNAME'))


# set up flask-login for user authentication
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# a class to represent a user
class User(flask_login.UserMixin):
    # inheriting from the UserMixin class gives this blank class default implementations of the necessary methods that flask-login requires all User objects to have
    # see some discussion of this here: https://stackoverflow.com/questions/63231163/what-is-the-usermixin-in-flask
    def __init__(self, data):
        '''
        Constructor for User objects
        @param data: a dictionary containing the user's data pulled from the database
        '''
        self.id = data['_id'] # shortcut to the _id field
        self.data = data # all user data from the database is stored within the data field

def locate_user(user_id=None, username=None):
    '''
    Return a User object for the user with the given id or username, or None if no such user exists.
    @param user_id: the user_id of the user to locate
    @param username: the username address of the user to locate
    '''
    if user_id:
        # loop up by user_id
        criteria = {"_id": ObjectId(user_id)}
    else:
        # loop up by username
        criteria = {"username": username}
    doc = Database.find_one('users',criteria) # find a user with the given criteria

    # if user exists in the database, create a User object and return it
    if doc:
        # return a user object representing this user
        user = User(doc)
        return user
    # else
    return None

@login_manager.user_loader
def user_loader(user_id):
    '''
    This function is called automatically by flask-login with every request the browser makes to the server.
    If there is an existing session, meaning the user has already logged in, then this function will return the logged-in user's data as a User object.
    @param user_id: the user_id of the user to load
    @return a User object if the user is logged-in, otherwise None
    '''
    return locate_user(user_id=user_id) # return a User object if a user with this user_id exists


# set up any context processors
# context processors allow us to make selected variables or functions available from within all templates

@app.context_processor
def inject_user():
    # make the currently-logged-in user, if any, available to all templates as 'user'
    return dict(user=flask_login.current_user)

@app.route('/')
def home():
    """
    Processes login and redirects accordingly if request was made
    Otherwise display login form
    """
    return(redirect(url_for("stories")))

@app.route('/login')
def login():
    """
    Processes login and redirects accordingly if request was made
    Otherwise display login form
    """
    # if the current user is already signed in, there is no need to sign up, so redirect them
    if flask_login.current_user.is_authenticated:
        flash('You are already logged in, silly!') # flash can be used to pass a special message to the template we are about to render
        return redirect(url_for('stories')) # tell the web browser to make a request for the / route (the home function)
    if (request.args):
        if bool(request.args["username"]) and bool(request.args["password"]):
            usernameInput = request.args["username"]
            passwordInput = request.args["password"]
            user = locate_user(username=usernameInput)
            if user:
                    if check_password_hash(user.data['password'], passwordInput):
                        flask_login.login_user(user)
                        return(redirect(url_for("home")))
                    else:
                        flash('Invalid password.')
                        return(redirect(url_for("login")))
            else:
                flash('No user found for username.')
                return(redirect(url_for("login")))
        else:
            flash('Please enter an username and password.')
            return(redirect(url_for("login")))
    else:
        return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route for the register page
    """
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':
        u = request.form['username']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        p = request.form['password']

        if not u or not p or not firstName or not lastName:
            flash('Please fill all fields.')
        elif locate_user(username=u):
            flash('An account was already created with this username.')
        else:
            hashed_password = generate_password_hash(p)
            Database.insert_one('users',{"username": u, 'firstName': firstName, 'lastName': lastName,  "password": hashed_password, "followers":0 , "following" : 0})
            flash('Success!')
            return redirect(url_for('login'))
    else:
        if flask_login.current_user.is_authenticated:
            flash('You are already logged in, silly!')
            return redirect(url_for('homepage'))
    return render_template("register.html")

@app.route('/stories')
def stories():
    u = None
    # print(flask_login.current_user, file=sys.stderr)
    shared_books = Database.find('books',{"shared": True})

    if hasattr(flask_login.current_user, "data"):
        u = flask_login.current_user.data['firstName']
        print(u, file=sys.stderr)

    return render_template("stories.html", username = u, books = shared_books)

@app.route('/book', methods = ['POST', 'GET'])
def book():
    u = None
    user = None
    if hasattr(flask_login.current_user, "data"):
        u = flask_login.current_user.data['firstName']
        user = flask_login.current_user.data['username']

    if request.method == 'POST':
        book_id = request.form['id']
        book = Database.find_one('books',{"_id" : ObjectId(book_id)})
        session["story"] = book["story"]
        session["book_id"] = book_id

    page = request.args.get('page', default = 0, type=int)

    response = openai.Image.create(
    prompt = session["story"][page],
    n=1,
    size="256x256"
    )
    image_url = response['data'][0]['url']

    return render_template("book.html", username = u, user = user, storyID = session["book_id"], url = image_url, content = session["story"][page], page = page, last_page = len(session["story"]))

@app.route('/create-book', methods = ['GET', 'POST'])
@flask_login.login_required
def create_book():
    u = flask_login.current_user.data['firstName']

    if request.method == 'POST':
        _id = Database.insert_one('books',{"title": session["title"], 'story': session["story"], 'shared' : False, 'liked' : [], "creator" : flask_login.current_user.data["_id"]})
        Database.update('users',{"_id": flask_login.current_user.data['_id']}, {'$push' : {'stories' : ObjectId(_id.inserted_id)}})
        return(redirect(url_for("private")))

    prompt = request.args.get('prompt')
    session["story"] = ["Enter Prompt To Generate Story!"]
    session["title"] = None
    if(prompt != None):
        response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Give a title with a story about {prompt}",
        temperature=0.8,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0
        )
        session["title"] = response["choices"][0]["text"].split("\n\n")[1]
        session["story"] = response["choices"][0]["text"].split("\n\n")[2:]

    return render_template("create_book.html", username = u, story=session["story"], title=session["title"])

@app.route('/private', methods = ['GET', 'POST'])
@flask_login.login_required
def private():
    u = flask_login.current_user.data['firstName']

    # if request.method == 'POST':
    #     db.users.updateOne({"username": flask_login.current_user.data['_id']}, {'$push' : {'stories' : { 'story' : session["story"], 'title' : session["title"]}}})
    #     return(redirect(url_for("stories")))
    #
    # prompt = request.args.get('prompt')
    # session["story"] = ["Enter Prompt To Generate Story!"]
    # session["title"] = None
    # if(prompt != None):
    #     response = openai.Completion.create(
    #     model="text-davinci-003",
    #     prompt=f"Give a title with a story about {prompt}",
    #     temperature=0.8,
    #     max_tokens=2048,
    #     top_p=1.0,
    #     frequency_penalty=0.5,
    #     presence_penalty=0.0
    #     )
    #     session["title"] = response["choices"][0]["text"].split("\n\n")[1]
    #     session["story"] = response["choices"][0]["text"].split("\n\n")[2:]
    books = get_private_books()
    user = Database.find_one('users',{"_id" : flask_login.current_user.data["_id"]})
    followers = user["followers"]
    following = user["following"]
    return render_template("private.html", username = u, books = books, followers = followers, following = following)

@app.route('/delete', methods = ['GET', 'POST'])
@flask_login.login_required
def delete():
    u = flask_login.current_user.data['firstName']
    book_id = request.form['id']
    Database.update('users', { "_id": flask_login.current_user.data["_id"] }, { "$pull": { "stories": ObjectId(book_id)} } )
    Database.delete('books',{"_id": ObjectId(book_id)})
    books = get_private_books()
    user = Database.find_one('users',{"_id" : flask_login.current_user.data["_id"]})
    followers = user["followers"]
    following = user["following"]
    return render_template("private.html", username = u, books = books, followers=followers, following = following)

@app.route('/share', methods = ['GET', 'POST'])
@flask_login.login_required
def share():
    u = flask_login.current_user.data['firstName']
    book_id = request.form['id']
    Database.update('books', { "_id": ObjectId(book_id) }, { "$set": { "shared": True} } )
    books = get_private_books()
    user = Database.find_one('users',{"_id" : flask_login.current_user.data["_id"]})
    followers = user["followers"]
    following = user["following"]
    return render_template("private.html", username = u, books = books, followers = followers, following = following)

@app.route('/unshare', methods = ['GET', 'POST'])
@flask_login.login_required
def unshare():
    u = flask_login.current_user.data['firstName']
    book_id = request.form['id']
    Database.update('books', { "_id": ObjectId(book_id) }, { "$set": { "shared": False} } )
    books = get_private_books()
    user = Database.find_one('users',{"_id" : flask_login.current_user.data["_id"]})
    followers = user["followers"]
    following = user["following"]
    return render_template("private.html", username = u, books = books, followers = followers, following = following)

def get_private_books():
    private_books = Database.find_one('users',{"_id": flask_login.current_user.data['_id']}, {"_id" : 0, "stories" : 1})['stories']
    books = []
    for book_id in private_books:
        book = Database.find_one('books',{"_id" : book_id})
        books.append(book)
    return books

@app.route('/logout')
@flask_login.login_required
def logout():
    """
    Route to logout
    """
    flask_login.logout_user()
    return(redirect(url_for("stories")))

@app.route('/api/countLike', methods = ['POST'])
@flask_login.login_required
@cross_origin()
def countLike():
    input = request.get_json()
    username = input['username']
    storyID = ObjectId(input['storyID'])
    temp = Database.find_one('books',{"_id": storyID})
    b = loads(dumps(temp))
    num = len(b['likes'])
    has = username in b['likes']
    data = {
        "count" : num,
        "contains" : has,
    }
    return jsonify(data), 200, {'Content-Type': 'application/json'}

@app.route('/api/updateLike', methods = ['POST'])
@flask_login.login_required
@cross_origin()
def updateLike():
    input = request.get_json()
    print(input, file=sys.stderr)
    username = input['username']
    storyID = ObjectId(input['storyID'])
    temp = Database.find_one('books',{"_id": storyID})
    b = loads(dumps(temp))
    if username in b['likes']:
        Database.update('books',{"_id": storyID}, {'$pull': {'likes': username}})
    else:
        Database.update('books',{"_id": storyID}, {'$push': {'likes': username}})
    temp = Database.find_one('books',{"_id": storyID})
    b = loads(dumps(temp))
    num = len(b['likes'])
    has = username in b['likes']
    data = {
        "count" : num,
        "contains" : has,
    }
    return jsonify(data), 200, {'Content-Type': 'application/json'}

@app.route('/profile', methods = ['GET', 'POST'])
@flask_login.login_required
def profile():
    u = flask_login.current_user.data['firstName']
    user = Database.find_one('users',{"_id" : flask_login.current_user.data["_id"]})
    followers = user["followers"]
    following = user["following"]
    books_result = Database.find('books',{"creator" : flask_login.current_user.data["_id"], "shared": True})
    if books_result is None:
        books=[]
    else:
        books=list(books_result)
    return render_template("profile.html", username = u, books = books, followers = followers, following = following, profile_name = user["firstName"])

if __name__=='__main__':
    #app.run(debug=True)
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
