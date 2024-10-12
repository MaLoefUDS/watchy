
import sqlite3
import hashlib
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
                 (username TEXT, list_id TEXT)''')
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

def extract_id(url):
    if "v=" in url:
        return url.split('v=')[-1].split('&')[0]
    else:
        return url.split('/')[-1].split('?')[0]


def add_video(username, url):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO videos VALUES (?, ?, 0)", (username, extract_id(url)))
    conn.commit()
    conn.close()


def video_exists(username, url):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE username = ? AND identifier = ?", (username, extract_id(url)))
    video = c.fetchone()
    conn.close()
    return video


def update_video(username, video_id, new_state):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if new_state == video_state['delete']:
        c.execute("DELETE FROM videos WHERE username = ? AND identifier = ?", (username, video_id))
    else:
        c.execute("UPDATE videos SET state = ? WHERE username = ? AND identifier = ?", (new_state, username, video_id))
    conn.commit()
    conn.close()


def get_videos(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT identifier, state FROM videos WHERE username = ?", (username, ))
    videos = c.fetchall()
    conn.close()
    return videos

