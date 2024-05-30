from datetime import datetime
import sqlite3
from typing import Literal
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from utils.teams import parseTeam, teamExists
from utils.leagues import createLeague, getLeague, parseLeague

def parseTeamMatch(teamId: str, side: Literal['home', 'away'], source: BeautifulSoup, connection: sqlite3.Connection) -> int:
  cursor = connection.cursor()
  
  goals = source.select('.detailScore__wrapper span')[0 if side == 'home' else -1].get_text(strip=True)
  expectedGoals = None
  ballPossession = None
  shotsTotal = None
  shotsOnGoal = None
  freeKicks = None
  corners = None
  offsides = None
  goalieSaves = None
  fouls = None
  yellowCards = None
  redCards = None
  passes = None
  attacks = None
  dangerousAttacks = None

  try:
      expectedGoals = source.select_one('[data-testid="wcl-statistics"]:contains("Očakávané góly")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      ballPossession = source.select_one('[data-testid="wcl-statistics"]:contains("Držanie lopty")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True).removesuffix('%')
  except AttributeError:
      pass

  try:
      shotsTotal = source.select_one('[data-testid="wcl-statistics"]:contains("Strely celkom")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      shotsOnGoal = source.select_one('[data-testid="wcl-statistics"]:contains("Strely na bránku")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      freeKicks = source.select_one('[data-testid="wcl-statistics"]:contains("Priame kopy")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      corners = source.select_one('[data-testid="wcl-statistics"]:contains("Rohové kopy")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      offsides = source.select_one('[data-testid="wcl-statistics"]:contains("Ofsajdy")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      goalieSaves = source.select_one('[data-testid="wcl-statistics"]:contains("Zákroky brankárov")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      fouls = source.select_one('[data-testid="wcl-statistics"]:contains("Fauly")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      yellowCards = source.select_one('[data-testid="wcl-statistics"]:contains("Žlté karty")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      redCards = source.select_one('[data-testid="wcl-statistics"]:contains("Červené karty")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      passes = source.select_one('[data-testid="wcl-statistics"]:contains("Prihrávok celkom")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      attacks = source.select_one('[data-testid="wcl-statistics"]:contains("Útoky")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass

  try:
      dangerousAttacks = source.select_one('[data-testid="wcl-statistics"]:contains("Nebezpečné útoky")').select('[data-testid="wcl-statistics-value"]')[0 if side == 'home' else -1].get_text(strip=True)
  except AttributeError:
      pass
  
  
  cursor.execute("""
                 INSERT INTO teamMatchStats 
                 (team, goals, expectedGoals, ballPossession, shotsTotal, shotsOnGoal, freeKicks, corners, offsides, goalieSaves, fouls, yellowCards, redCards, passes, attacks, dangerousAttacks) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                 """, 
                 (teamId, goals, expectedGoals, ballPossession, shotsTotal, shotsOnGoal, freeKicks, corners, offsides, goalieSaves, fouls, yellowCards, redCards, passes, attacks, dangerousAttacks))
  connection.commit()
  return cursor.lastrowid

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

  accept_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
  )
  accept_button.click()

  # Wait for the cookie banner to be removed
  WebDriverWait(driver, 10).until(
    EC.invisibility_of_element_located((By.ID, 'onetrust-banner-sdk'))
  )

  show_more_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.showMore[href="#/prehlad-zapasu/statistiky-zapasu"]'))
  )
  # Click the button
  show_more_button.click()
  # Wait until statistics are shown
  WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="wcl-statistics"]'))
  )

  parsed = BeautifulSoup(driver.page_source, 'html.parser')

  homeTeamId = parsed.select_one('.duelParticipant__home .participant__participantName a').attrs['href'].rstrip('/').split('/')[-1]
  if not teamExists(homeTeamId, connection):
    parseTeam(parsed.select_one('.duelParticipant__home .participant__participantName a').attrs['href'], connection)

  awayTeamId = parsed.select_one('.duelParticipant__away .participant__participantName a').attrs['href'].rstrip('/').split('/')[-1]
  if not teamExists(awayTeamId, connection):
    parseTeam(parsed.select_one('.duelParticipant__away .participant__participantName a').attrs['href'], connection)

  leagueUrl = parsed.select_one('.tournamentHeader__country a').attrs['href'].rstrip('/')
  leagueId = getLeague(urlName='/'.join(leagueUrl.rstrip('/').split('/')[1:]), connection=connection)
  if leagueId is None:
    leagueId = parseLeague(leagueUrl, connection)

  dateTimeStart = parsed.select_one('.duelParticipant__startTime').get_text(strip=True)
  dateObj = datetime.strptime(dateTimeStart, "%d.%m.%Y %H:%M")
  formattedDateTime = dateObj.strftime("%Y-%m-%d %H:%M")

  homeId = parseTeamMatch(teamId=homeTeamId, side='home', source=parsed, connection=connection)
  awayId = parseTeamMatch(teamId=awayTeamId, side='away', source=parsed, connection=connection)

  cursor = connection.cursor()
  cursor.execute("INSERT INTO matches (matchId, leagueId, homeTeam, awayTeam, dateTime) VALUES (?, ?, ?, ?, ?)", (matchId, leagueId, homeId, awayId, formattedDateTime))
  connection.commit()
