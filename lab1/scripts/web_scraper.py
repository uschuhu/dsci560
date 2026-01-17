import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]   # lab1/
DATA_DIR = BASE_DIR / "data"

url = 'https://www.cnbc.com/world/?region=world'

# response = requests.get(url)
# soup = BeautifulSoup(response.content, 'html.parser')


# market_banner = soup.find("div", id="HomePageInternational-MarketsBanner-1-panel")
# print(market_banner)

from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome()
driver.get("https://www.cnbc.com/world/?region=world")

time.sleep(5) # wait for page to load

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

market_banner = soup.find("div", id="HomePageInternational-MarketsBanner-1-panel")
latest_news = soup.find("div", class_="LatestNews-isHomePage LatestNews-isIntlHomepage")


with open(DATA_DIR / "raw_data" / "web_data.html", "w", encoding="utf-8") as f:
    f.write("<html><body>\n")
    f.write(market_banner.prettify())
    f.write("\n")
    f.write(latest_news.prettify())
    f.write("\n</body></html>")