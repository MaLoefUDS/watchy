
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
from backend import *
import hashlib

app = Flask(__name__)
app.secret_key = "watchy motchy"


@app.route("/")
def main():
    username = session.get("username")
    if username:
        return render_template('index.html', username=username)
    else:
        return render_template('login.html')


@app.route("/login", methods=['GET', 'POST'])
def login():

    # serve login page
    if request.method == 'GET':
        return render_template('login.html')

    # login user
    else:
        username = request.form['username']
        password = request.form['password']

        if check_login(username, password):
            session["username"] = username
            return render_template('index.html', username=username)
        else:
            return render_template('login.html', error="Invalid username or password")


@app.route("/register", methods=['GET', 'POST'])
def register():

    # serve register page
    if request.method == 'GET':
        return render_template('register.html')

    # register user
    else:
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password-confirmation']

        if user_exists(username):
            return render_template('register.html', username_error="Username already exists")

        if password != password_confirm:
            return render_template('register.html', password_confirmation_error="Passwords do not match")

        add_user(username, password)
        return render_template('index.html', username=username)


@app.route("/upload", methods=['POST'])
def upload():

    username = session.get("username")
    if not username:
        return render_template('login', error="You must be logged in to upload a video")

    # add url to users list
    url = request.form['url']
    if validate_url(url):
        return render_template('index.html', username=username)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
