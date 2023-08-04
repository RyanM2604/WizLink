import os
from cs50 import SQL
import datetime
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import requests
from email_validator import validate_email, EmailNotValidError

# App object config
app = Flask(__name__)

app.debug = True

# Session impermanence config
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database config with cs50 library
db = SQL("sqlite:///main.db")  # Change this

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
        return redirect("/home")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/call", methods= ["GET", "POST"])
def call():
    if request.method == "GET":
        return render_template("room_list.html")
    elif request.method == "POST":
        room_name = request.form.get("room_name")
        hostname = request.form.get("hostname")

        rows = db.execute("SELECT * FROM users WHERE role = ? AND id = ?", "expert", session["user_id"])
        if len(rows) == 0:
            return apology("Not an expert, Forbidden", 403)
        else:
            db.execute("INSERT INTO rooms (room_name, host_name, user_id) VALUES (?, ?, ?)", room_name, hostname, session["user_id"])
        
        rooms = db.execute("SELECT * FROM rooms ORDER BY host_name")
        return render_template("room_list.html", rooms=rooms)

@app.route("/publish")
def publish():
    return apology("Under Construction!", 403)

@app.route("/leaderboard")
def leaderboard():
    return apology("Under Construction!", 403)

@app.route("/awards")
def awards():
    return apology("Under Construction!", 403)