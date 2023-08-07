import os
import uuid  # for generating random user id values

from datetime import datetime, timezone
from cs50 import SQL
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from email_validator import validate_email, EmailNotValidError
import twilio.jwt.access_token
import twilio.jwt.access_token.grants
import twilio.rest

# App object config
app = Flask(__name__)

app.debug = True

# Load environment variables from a .env secure file
load_dotenv()

# Create a Twilio client
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
api_key = os.environ["TWILIO_API_KEY_SID"]
api_secret = os.environ["TWILIO_API_KEY_SECRET"]
twilio_client = twilio.rest.Client(api_key, api_secret, account_sid)

# Session impermanence config
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database config with cs50 library
db = SQL("sqlite:///main.db") 


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///main.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def apology(text, error_code):
    return render_template("apology.html", text=text, error_code=error_code)

@app.after_request
def after_request(response):
    """Ensuring responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

"""
This can be used to clear leaderboards in required

def clear_expired():
    current = datetime.datetime.now()
    one_week_ago = current - datetime.timedelta(days=7)
    db.execute("DELETE FROM exercise_time WHERE user_id = ? AND timestamp = ?", session["user_id"], one_week_ago)
"""

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        # Getting form variables
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form["role"]
        print(role)
        gender = request.form.get("gender").lower()
        check = request.form.get("confirmation")
        email = request.form.get("email")

        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized

        except EmailNotValidError as e:
            return apology(e, 403)


        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Checking for misinput
        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not check:
            return apology("must provide password confirmation", 400)
        elif password != check:
            return apology("passwords don't match", 403)
        elif len(rows) > 0:
            return apology("username exists", 403)
        else:
            # Entering a new user in database
            pass_hash = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash, email, role, gender) VALUES (?, ?, ?, ?, ?)", username, pass_hash, email, role, gender)
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
            session["user_id"] = rows[0]["id"]
            flash('You were successfully logged in')
            return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/call", methods=["GET", "POST"])
def call():
    if request.method == "GET":
        rooms = db.execute("SELECT * FROM rooms ORDER BY host_name")
        return render_template("room_list.html", rooms=rooms)
    elif request.method == "POST":
        room_name = request.form.get("room-name-input")
        hostname = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE id = ? AND role = ?", session["user_id"], 'Expert')
        print("Here is the row")
        print(rows)
        if len(rows) == 0:
            pass
        else:
            db.execute("INSERT INTO rooms (room_name, host_name, user_id) VALUES (?, ?, ?)", room_name, hostname, session["user_id"])

        current = db.execute("SELECT points FROM users WHERE id = ?", session["user_id"])[0]["points"]
        db.execute("UPDATE users SET points = ? WHERE id = ?", (current + 10), session["user_id"])

        rooms = db.execute("SELECT * FROM rooms ORDER BY host_name")
        response_data = {"message": "Success"}
        return jsonify(response_data)

def find_or_create_room(room_name):
    try:
        twilio_client.video.v1.rooms(room_name).fetch()
    except twilio.base.exceptions.TwilioRestException:
        twilio_client.video.v1.rooms.create(unique_name=room_name, type="go")


def get_access_token(room_name):
    access_token = twilio.jwt.access_token.AccessToken(
        account_sid, api_key, api_secret, identity=uuid.uuid4().int
    )
    video_grant = twilio.jwt.access_token.grants.VideoGrant(room=room_name)
    access_token.add_grant(video_grant)
    return access_token

@app.route("/join-room", methods=["POST"])
def join_room():
    room_name = request.json.get("room_name")
    find_or_create_room(room_name)
    access_token = get_access_token(room_name)
    return {"token": access_token.to_jwt()}

@app.route("/delete-room", methods=["POST"])
def delete_room():
    room_name = request.json.get("roomName")
    print(f"Received request to delete room: {room_name}")
    
    db.execute("DELETE FROM rooms WHERE room_name = ?", room_name)
    print(f"Deleted room: {room_name}")
    json_response = {"deletion": "Success"}
    return jsonify(json_response)

@app.route("/publish")
def publish():
    if request.method == "GET":
        return render_template("publish.html")
    elif request.method == "POST":
        # Getting form variables
        title = request.form.get("title")
        content = request.form.get("content")
        user_id = db.execute("SELECT id FROM users WHERE id = ?", session["user_id"])
        author = db.execute("SELECT username FROM users WHERE id = ?", user_id[0]["id"])
        time_posted = datetime.now().strftime("%d/%m/%Y")

        if not title:
            return apology("must provide title", 400)
        elif not content:
            return apology("must provide content", 400)
        else: 
            # Entering a new post in database
            db.execute("INSERT INTO posts (user_id, time, author, title, content) VALUES (?, ?, ?, ?, ?)", user_id[0]["id"], time_posted, author[0]["username"], title, content)
            flash('posted successfully')
            return redirect("/guides")

@app.route("/guides")
def guides():
    posts_list = db.execute("SELECT * FROM posts")
    return render_template('guides.html', guides = posts_list)

@app.route("/post/<pid>")
def post(pid):
    guide = db.execute("SELECT * FROM posts WHERE post_id = ?", pid)
    return render_template("post.html", post = guide)

@app.route("/leaderboard")
def leaderboard():
    rows = db.execute("SELECT * FROM users ORDER BY points DESC LIMIT 10")
    return render_template("leaderboard.html", rows=rows)

@app.route("/awards")
def awards():
    points = db.execute("SELECT points FROM users WHERE id = ?", session["user_id"])[0]["points"]
    return render_template("awards.html", points=points)