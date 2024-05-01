import re
import sqlite3
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from utils.teams import parseTeam, teamExists
from utils.leagues import createLeague, getLeague


def parseMatch(matchId: str, connection: sqlite3.Connection) -> None:
  url = f'https://www.flashscore.sk/zapas/{matchId}'
  options = Options()
  options.add_argument("--headless")
  options.add_argument("--disable-gpu")
  options.add_argument("--no-sandbox")

  driver = webdriver.Chrome(options=options)
  driver.get(url)
  WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CLASS_NAME, 'duelParticipant__home'))
  )
  parsed = BeautifulSoup(driver.page_source, 'html.parser')

  homeTeamId = parsed.select_one('.duelParticipant__home .participant__participantName a').attrs['href'].rstrip('/').split('/')[-1]
  if not teamExists(homeTeamId, connection):
    parseTeam(parsed.select_one('.duelParticipant__home .participant__participantName a').attrs['href'], connection)

  awayTeamId = parsed.select_one('.duelParticipant__away .participant__participantName a').attrs['href'].rstrip('/').split('/')[-1]
  if not teamExists(awayTeamId, connection):
    parseTeam(parsed.select_one('.duelParticipant__away .participant__participantName a').attrs['href'], connection)

  leagueUrl = parsed.select_one('.tournamentHeader__country a').attrs['href'].rstrip('/')
  league = getLeague(urlName=leagueUrl.split('/')[-1], connection=connection)
  if league is None:
    country = parsed.select_one('.tournamentHeader__country').getText(strip=True).split(':')[0]
    league = createLeague(connection=connection, country=country, urlName=leagueUrl.split('/')[-1], name='TODO')

  cursor = connection.cursor()
  cursor.execute("INSERT INTO matches (leagueId, homeTeam, awayTeam) VALUES (?, ?, ?)", (league.id, homeTeamId, awayTeamId))
  connection.commit()

  # TODO parse all stats.