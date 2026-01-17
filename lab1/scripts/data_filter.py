import csv
from bs4 import BeautifulSoup
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]   # lab1/
DATA_DIR = BASE_DIR / "data"

file_name = "web_data.html"
with open(DATA_DIR / "raw_data" / file_name, "r", encoding="utf-8") as f:   
    html_content = f.read()
print("Reading html from", file_name)
soup = BeautifulSoup(html_content, 'html.parser')

# market_data.csv
market_card = soup.find_all("a", class_="MarketCard-container")
print("Filtering market data")
data = []
for card in market_card:
    symbol = card.find("span", class_="MarketCard-symbol").text.strip()
    price = card.find("span", class_="MarketCard-stockPosition").text.strip()
    change = card.find("span", class_="MarketCard-changesPct").text.strip()
    data.append((symbol, price, change))
print("Writing to market_data.csv")
with open(DATA_DIR / "processed_data" / "market_data.csv", "w", newline="", encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["symbol", "price", "change"])
    writer.writerows(data)

# latest_news.csv
latest_news = soup.find_all("li", class_="LatestNews-item")
print("Filtering latest news data") 
data = []
for news in latest_news:
    timestamp = news.find("time", class_="LatestNews-timestamp").text.strip()
    title = news.find("a", class_="LatestNews-headline").text.strip()
    link = news.find("a", class_="LatestNews-headline")["href"].strip()
    data.append((timestamp, title, link))
print("Writing to news_data.csv")
with open(DATA_DIR / "processed_data" / "news_data.csv", "w", newline="", encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "title", "link"])
    writer.writerows(data)