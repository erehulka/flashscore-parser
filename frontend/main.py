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
    avgEffectivity = round(cursor.fetchone()[0], 2)

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

    cursor.execute("SELECT COUNT(*) FROM matches")
    parsedMatches = cursor.fetchone()[0]

    return render_template('main.html', leagues=leagues, avgEffectivity=avgEffectivity, avgEffectivityPerDay=avgEffectivityPerDay, parsedMatches=parsedMatches)

@app.route('/league/<league_id>')
def league(league_id):
    cursor: sqlite3.Cursor = g.db.cursor()
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

    cursor.execute("""
                   SELECT urlName, country, name FROM leagues WHERE id = ?
                   """, (league_id,))
    league_info = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM matches WHERE leagueId = ?", (league_id,))
    parsedMatches = cursor.fetchone()[0]

    return render_template('league.html', teams=teams, league_id=league_id, league_info=league_info, parsedMatches=parsedMatches)

@app.route('/team/<league_id>/<team_id>')
def team(league_id, team_id):
    cursor = g.db.cursor()
    cursor.execute("""
                   SELECT m.matchId, tHome.name, tAway.name, tmsHome.goals, tmsAway.goals
                   FROM matches m
                   JOIN teamMatchStats tmsHome ON tmsHome.id = m.homeTeam
                   JOIN teamMatchStats tmsAway ON tmsAway.id = m.awayTeam
                   JOIN teams tHome ON tHome.id = tmsHome.team
                   JOIN teams tAway ON tAway.id = tmsAway.team
                   WHERE tHome.id = ? OR tAway.id = ?
                   ORDER BY m.dateTime DESC
                   LIMIT 5
                   """, (team_id, team_id))
    last5Matches = []
    for row in cursor:
        last5Matches.append({
            "matchId": row[0],
            "homeTeam": row[1],
            "awayTeam": row[2],
            "homeGoals": row[3],
            "awayGoals": row[4],
        })

    tenDaysAgo = (datetime.today() - timedelta(days=10)).strftime('%Y-%m-%d')
    cursor.execute(
        """
            SELECT SUBSTR(m.dateTime, 1, 10) as date, AVG(tms.goals / tms.expectedGoals) as avg_effectivity
            FROM teamMatchStats tms
            JOIN matches m ON m.homeTeam = tms.id OR m.awayTeam = tms.id
            WHERE date >= ? AND tms.expectedGoals IS NOT NULL and tms.expectedGoals > 0 AND tms.team = ?
            GROUP BY date
            ORDER BY date
        """,
        (tenDaysAgo, team_id)
    )
    avgEffectivityPerDay = {}
    for row in cursor:
        avgEffectivityPerDay[row[0]] = row[1]

    cursor.execute("""
                    SELECT 
                        AVG(tms.goals / tms.expectedGoals) as avg_effectivity, 
                        AVG(tms.shotsTotal), 
                        AVG(tms.shotsOnGoal), 
                        AVG(tms.fouls), 
                        AVG(tms.yellowCards), 
                        AVG(tms.redCards),
                        AVG(tms.passes)
                    FROM teamMatchStats tms
                    WHERE tms.expectedGoals IS NOT NULL and tms.expectedGoals > 0 AND tms.team = ?
                   """, (team_id,))
    fetched = cursor.fetchone()
    averageStats = {
        'effectivity': round(fetched[0] or 0, 2),
        'shotsTotal': round(fetched[1] or 0, 2),
        'shotsOnGoal': round(fetched[2] or 0, 2),
        'fouls': round(fetched[3] or 0, 2),
        'yellowCards': round(fetched[4] or 0, 2),
        'redCards': round(fetched[5] or 0, 2),
        'passes': round(fetched[6] or 0, 2),
    }

    cursor.execute("""
                   SELECT urlName, name FROM teams WHERE id = ?
                   """, (team_id,))
    team_info = cursor.fetchone()

    cursor.execute("""
                   SELECT COUNT(*) FROM matches m
                   JOIN teamMatchStats tms ON tms.id = m.homeTeam OR tms.id = m.awayTeam
                   WHERE tms.team = ?
                   """
                   , (team_id,))
    parsedMatches = cursor.fetchone()[0]

    return render_template('team.html', last5Matches=last5Matches, league_id=league_id, avgEffectivityPerDay=avgEffectivityPerDay, averageStats=averageStats, team_info=team_info, parsedMatches=parsedMatches)


"""
TODO:
- if there is no value, for example for fouls, either not average, do not show the card with zero.
- Some more stats
"""