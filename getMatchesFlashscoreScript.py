import re
import sqlite3
import time
from selenium import webdriver # Selenium needed because of need to click buttons on the web
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from utils.parseMatch import parseMatch
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='log/error.log', encoding='utf-8', level=logging.INFO)

# Configure browser options
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

# Navigate to the URL
url = "https://www.flashscore.sk/futbal"
driver.get(url)

# Dismiss any cookie consent or privacy notifications
try:
    cookie_consent = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-button-group")))
    cookie_consent.click()
    time.sleep(10)
except:
    logger.info("Cookie consent not found or error dismissing it")

# Click the "yesterday" button twice
try:
    yesterday_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "calendar__navigation--yesterday")))
    for _ in range(2):
        yesterday_button.click()
        time.sleep(5)
except Exception as e:
    logger.error("Error clicking yesterday button")
    logger.error(e)
    exit(1)

time.sleep(10)

html = driver.page_source
parsed = BeautifulSoup(html, 'html.parser')


matchIds: list[str] = []
matches = parsed.select('.event__match')
for match in matches:
    matchId = match.attrs['id'] # For example g_1_faTuORtF
    matchIdParsed = re.sub(r'^g_1_(.*)$', r'\1', matchId) # We need to get only faTuORtF
    matchIds.append(matchIdParsed)

connection = sqlite3.connect('matches.db')

for id in matchIds:
    try:
        parseMatch(id, connection=connection)
    except Exception as e:
        logger.error(f"Error when parsing match {id}: {e}")

connection.close()
driver.quit()
