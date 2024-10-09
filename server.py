
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from backend import *
import hashlib

app = Flask(__name__)


@app.route("/")
def main():
    if request.cookies.get("id"):
        return render_template('index.html')
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
        pw_hash = sha256(password)

        if is_registered(username, sha256(password)):
            resp = make_response(render_template('index.html'))
            resp.set_cookie('id', sha256(username), max_age=60*60*24*365)
            return resp
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

        add_user(username, sha256(password))
        return render_template('index.html')


@app.route("/upload", methods=['POST'])
def upload():

    # add url to users list
    url = request.form['url']
    if validate_url(url):
        return render_template('index.html', url=url)


if __name__ == "__main__":
    init_db()
    app.run()
