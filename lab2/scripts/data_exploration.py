import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import pdfplumber
import pytesseract
import time

def extract_csv(file_path):
    return pd.read_csv(file_path)

def extract_pdf():
    with pdfplumber.open("sample.pdf") as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_html(link):
    driver = webdriver.Chrome()
    driver.get(link)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def main():
    csv_data = extract_csv()
    pdf_data = extract_pdf()
    web_data = extract_html()

    

if __name__ == "__main__":
    main()