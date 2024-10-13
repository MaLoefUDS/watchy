
import sqlite3
import hashlib
import time
import os


domain = 'thevent.xyz'

def https_enabled():
    return os.path.exists(f'/etc/letsencrypt/live/{domain}/fullchain.pem') and \
           os.path.exists(f'/etc/letsencrypt/live/{domain}/privkey.pem')


def validate_url(url):
    return url.startswith('https://www.youtube.com/') or \
           url.startswith('https://youtube.com/') or \
           url.startswith('https://youtu.be/')


def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts
                 (username TEXT PRIMARY KEY, password TEXT, salt TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS lists
                 (username TEXT, list_id TEXT, role INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invites
                (list_id TEXT, role INTEGER DEFAULT 2, token TEXT, timestamp INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (list_id TEXT, video_id TEXT, state INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()


def sha256(input, salt):
    hash = hashlib.sha256()
    hash.update((input + salt).encode())
    return hash.hexdigest()


def generate_salt():
    return os.urandom(16).hex()


## -------- User management -------- ##

def add_user(username, password):
    salt = generate_salt()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO accounts VALUES (?, ?, ?)", (username, sha256(password, salt), salt))
    conn.commit()
    conn.close()


def user_exists(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE username = ?", (username, ))
    user = c.fetchone()
    conn.close()
    return user


def check_login(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # get salt from database
    c.execute("SELECT salt FROM accounts WHERE username = ?", (username, ))
    salt = c.fetchone()[0]

    # obtain salted hash of password
    pw_hash = sha256(password, salt)
    c.execute("SELECT * FROM accounts WHERE username = ? AND password = ?", (username, pw_hash))

    user = c.fetchone()
    conn.close()
    return user and user[1] == pw_hash


## -------- Video management -------- ##

video_state = {
    'pending': 0,
    'watch_together': 1,
    'watch_alone': 2,
    'delete': 3
}

list_roles = {
    'owner': 0,
    'editor': 1,
    'viewer': 2,
}

def extract_id(url):
    if "v=" in url:
        return url.split('v=')[-1].split('&')[0]
    else:
        return url.split('/')[-1].split('?')[0]


def add_list(username, list_name):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO lists VALUES (?, ?, 0)", (username, list_name))
    conn.commit()
    conn.close()


def create_invite(list_id, role):
    token = generate_salt()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO invites VALUES (?, ?, ?, ?)", (list_id, role, token, int(time.time())))
    conn.commit()
    conn.close()
    return token


def invite_valid(token):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT timestamp FROM invites WHERE token = ?", (token, ))
    invite = c.fetchone()
    conn.close()
    return invite and invite[0] + 14_400 > int(time.time()) # 6 hours


def remove_invite(token):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM invites WHERE token = ?", (token, ))
    conn.commit()
    conn.close()


def user_in_list(username, list_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM lists WHERE username = ? AND list_id = ?", (username, list_id))
    user = c.fetchone()
    conn.close()
    return user


def add_user_to_list(username, list_id, role):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO lists VALUES (?, ?, ?)", (username, list_id, role))
    conn.commit()
    conn.close()


def add_video(list_id, url):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO videos VALUES (?, ?, 0)", (list_id, extract_id(url)))
    conn.commit()
    conn.close()


def video_exists(list_id, url):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE list_id = ? AND video_id = ?", (list_id, extract_id(url)))
    video = c.fetchone()
    conn.close()
    return video


def list_exists(username, list_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM lists WHERE username = ? AND list_id = ?", (username, list_id))
    video_entry = c.fetchone()
    conn.close()
    return video_entry


def update_video(list_id, video_id, new_state):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if new_state == video_state['delete']:
        c.execute("DELETE FROM videos WHERE list_id = ? AND video_id = ?", (list_id, video_id))
    else:
        c.execute("UPDATE videos SET state = ? WHERE list_id = ? AND video_id = ?", (new_state, list_id, video_id))
    conn.commit()
    conn.close()


def delete_list(username, list_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM lists WHERE username = ? AND list_id = ?", (username, list_id))
    c.execute("DELETE FROM videos WHERE list_id = ?", (list_id, ))
    conn.commit()
    conn.close()


def get_videos(list_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT video_id, state FROM videos WHERE list_id = ?", (list_id, ))
    videos = c.fetchall()
    conn.close()
    return videos


def get_lists(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT list_id, role FROM lists WHERE username = ?", (username, ))
    lists = c.fetchall()
    conn.close()
    return lists


def get_invite(token):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT list_id, role FROM invites WHERE token = ?", (token, ))
    invite = c.fetchone()
    conn.close()
    return invite

