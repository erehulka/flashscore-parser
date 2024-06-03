import json
from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)

def connect_db():
    return sqlite3.connect('../matches.db')

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# From here todo

@app.route('/')
def home():
    cursor = g.db.cursor()
    cursor.execute("SELECT id, username FROM users ORDER BY lower(username)")
    users = []

    for row in cursor:
        users.append(row)
    return render_template('main.html', users=users)

@app.route('/user/<user_id>/')
def user(user_id):
    cursor = g.db.cursor()
    cursor.execute("SELECT title, content, datetime FROM comments WHERE userId = ? ORDER BY datetime DESC", (user_id,))
    comments = []
    for row in cursor:
        comments.append({'title': row[0], 'content': row[1], 'datetime': row[2]})

    cursor.execute("SELECT username, top10, top3SimilarUsers FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    top3SimilarUsers = []
    for similar in json.loads(user[2]):
        cursor.execute("SELECT username FROM users WHERE id = ?", (similar,))
        top3SimilarUsers.append((similar, cursor.fetchone()[0]))

    return render_template('user.html',
                           comments=comments,
                           user=user[0],
                           n_of_comments=len(comments),
                           top10=json.loads(user[1]),
                           similarUsers=top3SimilarUsers
                           )