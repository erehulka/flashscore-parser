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

@app.route('/')
def home():
    cursor = g.db.cursor()
    cursor.execute("SELECT id, country, name FROM leagues ORDER BY lower(country)")
    leagues = []
    for row in cursor:
        leagues.append(row)

    return render_template('main.html', leagues=leagues)

@app.route('/league/<league_id>')
def league(league_id):
    cursor = g.db.cursor()
    cursor.execute("""
                   SELECT DISTINCT t.id, t.name FROM teams t 
                   JOIN teamMatchStats tms ON tms.team = t.id 
                   JOIN matches m ON m.homeTeam = tms.id OR m.awayTeam = tms.id
                   WHERE m.leagueId = ? 
                   ORDER BY lower(name)
                   """, (league_id,))
    teams = []
    for row in cursor:
        teams.append(row)

    return render_template('league.html', teams=teams)

@app.route('/team/<team_id>')
def team(team_id):
    return render_template('team.html')