from flask import Flask, render_template, g
import sqlite3
from datetime import datetime, timedelta

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
    cursor: sqlite3.Cursor = g.db.cursor()
    cursor.execute("SELECT id, country, name FROM leagues ORDER BY lower(country)")
    leagues = []
    for row in cursor:
        leagues.append(row)

    cursor.execute("""
                    SELECT AVG(tms.goals / tms.expectedGoals) as avg_effectivity
                    FROM teamMatchStats tms
                    WHERE tms.expectedGoals IS NOT NULL and tms.expectedGoals > 0
                   """)
    avgEffectivity = cursor.fetchone()[0]

    tenDaysAgo = (datetime.today() - timedelta(days=10)).strftime('%Y-%m-%d')

    cursor.execute(
        """
            SELECT SUBSTR(m.dateTime, 1, 10) as date, AVG(tms.goals / tms.expectedGoals) as avg_effectivity
            FROM teamMatchStats tms
            JOIN matches m ON m.homeTeam = tms.id OR m.awayTeam = tms.id
            WHERE date >= ? AND tms.expectedGoals IS NOT NULL and tms.expectedGoals > 0
            GROUP BY date
            ORDER BY date
        """,
        (tenDaysAgo,)
    )
    avgEffectivityPerDay = {}
    for row in cursor:
        avgEffectivityPerDay[row[0]] = row[1]

    return render_template('main.html', leagues=leagues, avgEffectivity=avgEffectivity, avgEffectivityPerDay=avgEffectivityPerDay)

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

    return render_template('league.html', teams=teams, league_id=league_id)

@app.route('/team/<league_id>/<team_id>')
def team(league_id, team_id):
    cursor = g.db.cursor()
    cursor.execute("""
                   SELECT m.matchId
                   FROM matches m
                   JOIN teamMatchStats tms ON tms.id = m.homeTeam OR tms.id = m.awayTeam
                   JOIN teams t ON t.id = tms.team
                   WHERE t.id = ?
                   ORDER BY m.dateTime DESC
                   LIMIT 5
                   """, (team_id,))
    last5Matches = []
    for row in cursor:
        last5Matches.append(row)

    return render_template('team.html', last5Matches=last5Matches, league_id=league_id)