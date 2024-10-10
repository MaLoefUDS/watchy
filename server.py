
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

        if not check_login(username, password):
            return render_template('login.html', error="Invalid username or password")

        session["username"] = username
        return redirect(url_for('main'))


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


@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template('login.html')


@app.route("/upload", methods=['POST'])
def upload():

    username = session.get("username")
    if not username:
        return render_template('login', error="You must be logged in to upload a video")

    url = request.form['url']
    if not validate_url(url):
        return render_template('index.html', username=username, error="Invalid URL")

    if video_exists(username, url):
        return render_template('index.html', username=username, error="Video is already in your list")

    add_video(username, url)
    return redirect(url_for('main'))


@app.route("/update/<content>", methods=['GET'])
def update(content):

    username = session.get("username")
    if not username:
        return

    video_id, new_state = content.split('&')
    if not video_id or not new_state:
        return render_template('index.html', username=username, error="Invalid request")

    if not video_exists(username, video_id):
        return render_template('index.html', username=username, error="Video does not exist")

    if not new_state.isdigit():
        return render_template('index.html', username=username, error="Invalid state")
    else:
        new_state = int(new_state)

    if not new_state in video_state.values():
        return render_template('index.html', username=username, error="Invalid state")

    update_video(username, video_id, new_state)
    return render_template('index.html', username=username)


@app.route("/videos", methods=['GET'])
def videos():

    username = session.get("username")
    if not username:
        return render_template('login', error="You must be logged in to view videos")

    # get videos from database
    return { "videos": get_videos(username) }


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8080)
