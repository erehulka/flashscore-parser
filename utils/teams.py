from dataclasses import dataclass
import sqlite3

from bs4 import BeautifulSoup
import requests

@dataclass
class Team:
  id: str
  country: str
  name: str
  urlName: str

def teamExists(id: str, connection: sqlite3.Connection) -> bool:
  cursor = connection.cursor()

  cursor.execute("SELECT * FROM teams WHERE id = ?", (id,))
  count = len(cursor.fetchall())
  
  return count > 0

def createTeam(team: Team, connection: sqlite3.Connection) -> None:
  cursor = connection.cursor()

  cursor.execute("INSERT INTO teams VALUES(?, ?, ?, ?)", (team.id, team.country, team.name, team.urlName))

  connection.commit()

def parseTeam(urlAdd: str, connection: sqlite3.Connection) -> None:
  url = f'https://www.flashscore.sk{urlAdd}'
  text = requests.get(url).text
  parsed = BeautifulSoup(text, 'html.parser')

  team = Team(
    id=urlAdd.rstrip('/').split('/')[-1],
    country=parsed.select('.breadcrumb__link')[-1].get_text(strip=True),
    name=parsed.select_one('.heading__name').get_text(strip=True),
    urlName='/'.join(urlAdd.rstrip('/').split('/')[1:])
  )
  createTeam(team, connection)