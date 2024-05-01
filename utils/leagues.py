from dataclasses import dataclass
import sqlite3
from typing import Optional

@dataclass
class League:
  id: str
  country: str
  name: str
  urlName: str

def getLeague(urlName: str, connection: sqlite3.Connection) -> Optional[League]:
  cursor = connection.cursor()

  cursor.execute("SELECT * FROM leagues WHERE urlName = ?", (urlName,))
  league = cursor.fetchone()
  if league is None:
    return None
  
  return League(id=league[0], country=league[1], name=league[2], urlName=league[3])

def createLeague(country: str, name: str, urlName: str, connection: sqlite3.Connection) -> League:
  cursor = connection.cursor()

  cursor.execute("INSERT INTO leagues (country, name, urlName) VALUES(?, ?, ?)", (country, name, urlName))
  newId = cursor.lastrowid
  connection.commit()

  return League(id=newId, country=country, name=name, urlName=urlName)