
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
from backend import *
import hashlib

app = Flask(__name__)
app.secret_key = "watchy motchy"


@app.route("/")
def main():
    username = session.get("username")
    if username:
        return render_template('lists.html', username=username)
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
        return redirect(url_for('main'))


@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template('login.html')


@app.route("/api/create-invite", methods=['GET'])
def invite():

    username = session.get("username")
    if not username:
        return { "invite": "" }

    list_id = request.args.get('list_id')
    role = request.args.get('role')
    if not list_id or not role:
        return { "invite": "" }

    if not list_exists(username, list_id):
        return { "invite": "" }

    token = create_invite(list_id, role)
    return { "invite": token }


@app.route("/api/join-list", methods=['GET'])
def join_list():

    username = session.get("username")
    if not username:
        return render_template('login.html', error="You must be logged in to join a list")

    token = request.args.get('token')
    if not token:
        return render_template('lists.html', username=username, error="Invalid request")

    if not invite_valid(token):
        return render_template('lists.html', username=username, error="Invite is invalid or expired")
    invite = get_invite(token)

    if user_in_list(username, invite[0]):
        return render_template('lists.html', username=username, error="You are already in this list")

    add_user_to_list(username, invite[0], invite[1])
    remove_invite(token)
    return redirect(url_for('main'))


@app.route("/create-list", methods=['POST'])
def form_create_list():
    name = request.form['list-name']
    return create_list(name)


@app.route("/api/create-list", methods=['GET', 'POST'])
def api_create_list():
    name = request.args.get('list-name')
    return create_list(name)


@app.route("/view-list", methods=['GET'])
def view_list():

    username = session.get("username")
    if not username:
        return render_template('login.html', error="You must be logged in to view lists")

    list_id = request.args.get('list_id')
    if not list_id:
        return render_template('lists.html', username=username, error="Invalid request")

    role = get_role(username, list_id)
    return render_template('videos.html', username=username, list_id=list_id, role=role)


# Common function for both create lists from api and from query parameters
def create_list(name):

    username = session.get("username")
    if not username:
        return render_template('login.html', error="You must be logged in to create a list")

    if not name:
        return render_template('lists.html', username=username, error="Invalid list name")

    if list_exists(username, name):
        return render_template('lists.html', username=username, error="List already exists")

    add_list(username, name)
    return redirect(url_for('main'))


@app.route("/api/delete-list", methods=['GET'])
def api_delete_list():

    username = session.get("username")
    if not username:
        return render_template('login.html', error="You must be logged in to delete a list")

    list_id = request.args.get('list_id')
    if not list_id:
        return render_template('lists.html', username=username, error="No list selected")

    if not list_exists(username, list_id):
        return render_template('lists.html', username=username, error="List does not exist")

    delete_list(username, list_id)
    return redirect(url_for('main'))


@app.route("/upload-video", methods=['POST'])
def form_upload_video():
    list_id = request.form['list_id']
    url = request.form['url']
    return upload_video(list_id, url)


@app.route("/api/upload-video", methods=['GET', 'POST'])
def api_upload_video():
    list_id = request.args.get('list_id')
    url = request.args.get('url')
    return upload_video(list_id, url)


# Common function for both upload from api and from query parameters
def upload_video(list_id, url):

    username = session.get("username")
    if not username:
        return render_template('login.html', error="You must be logged in to upload a video")

    role = get_role(username, list_id)
    if not validate_url(url):
        return render_template('videos.html', username=username, list_id=list_id, role=role, error="Invalid URL")

    if video_exists(list_id, url):
        return render_template('videos.html', username=username, list_id=list_id, role=role, error="Video is already in your list")

    add_video(list_id, url)
    return render_template('videos.html', username=username, list_id=list_id, role=role)


@app.route("/api/update-video", methods=['GET', 'POST'])
def api_update_video():

    username = session.get("username")
    if not username:
        return

    list_id = request.args.get('list_id')
    video_id = request.args.get('video_id')
    state = request.args.get('state')

    if not video_id or not state:
        return render_template('lists.html', username=username, error="Invalid request")

    if not user_in_list(username, list_id):
        return render_template('lists.html', username=username, error="You are not in this list")
    role = get_role(username, list_id)

    if not video_exists(list_id, video_id):
        return render_template('videos.html', username=username, list_id=list_id, role=role, error="Video does not exist")

    if not state.isdigit():
        return render_template('videos.html', username=username, list_id=list_id, role=role, error="Invalid state")
    state = int(state)

    if not state in video_state.values():
        return render_template('videos.html', username=username, list_id=list_id, role=role, error="Invalid state")

    if role != list_roles['owner'] and role != list_roles['editor']:
        return render_template('videos.html', username=username, list_id=list_id, role=role, error="You do not have permission to modify this list")

    update_video(list_id, video_id, state)
    return render_template('videos.html', username=username, list_id=list_id, role=role)


@app.route("/api/videos", methods=['GET'])
def videos():

    if not session.get("username"):
        return { "videos": [] }

    list_id = request.args.get('list_id')
    if not list_id:
        return { "videos": [] }

    if not user_in_list(session.get("username"), list_id):
        return { "videos": [] }

    # get videos from database
    return { "videos": get_videos(list_id) }


@app.route("/api/lists", methods=['GET'])
def lists():

    username = session.get("username")
    if not username:
        return { "lists": [] }

    # get lists from database
    return { "lists": get_lists(username) }


if __name__ == "__main__":
    init_db()

    if https_enabled():
        app.run(debug=True, host='0.0.0.0', port=8080, ssl_context=(f'/etc/letsencrypt/live/{domain}/fullchain.pem', f'/etc/letsencrypt/live/{domain}/privkey.pem'))
    else:
        app.run(debug=True, host='0.0.0.0', port=8080)
