from dataclasses import dataclass
import sqlite3
from typing import Optional

from bs4 import BeautifulSoup
import requests

@dataclass
class League:
  id: str
  country: str
  name: str
  urlName: str

def getLeague(urlName: str, connection: sqlite3.Connection) -> Optional[int]:
  cursor = connection.cursor()

  cursor.execute("SELECT id FROM leagues WHERE urlName = ?", (urlName,))
  league = cursor.fetchone()
  if league is None:
    return None
  
  return league[0]

def parseLeague(urlAdd: str, connection: sqlite3.Connection) -> int:
  url = f'https://www.flashscore.sk{urlAdd}'
  text = requests.get(url).text
  parsed = BeautifulSoup(text, 'html.parser')

  return createLeague(country=parsed.select('.breadcrumb__link')[-1].get_text(strip=True), name=parsed.select_one('.heading__name').get_text(strip=True), urlName='/'.join(urlAdd.rstrip('/').split('/')[1:]), connection=connection)

def createLeague(country: str, name: str, urlName: str, connection: sqlite3.Connection) -> int:
  cursor = connection.cursor()

  cursor.execute("INSERT INTO leagues (country, name, urlName) VALUES(?, ?, ?)", (country, name, urlName))
  newId = cursor.lastrowid
  connection.commit()

  return newId