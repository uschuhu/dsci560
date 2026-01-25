import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pdfplumber
import pytesseract
import time
import sys
import os

def extract_csv(file_path):
    return pd.read_csv(file_path)

def extract_pdf(soup, output_dir):
    import re
    from PIL import Image
    from io import BytesIO

    os.makedirs(output_dir, exist_ok=True)

    def extract_image_urls(soup):
        image_urls = set()

        main_img = soup.select_one("#imgTagWrapperId img")
        if main_img and main_img.get("src"):
            image_urls.add(main_img["src"])

        for img in soup.select("#altImages img"):
            src = img.get("src")
            if src:
                image_urls.add(src)

        for img in soup.select("#imageBlock img"):
            src = img.get("src")
            if src:
                image_urls.add(src)

        return list(image_urls)
    
    # functions to help OCR: get higher resolution images, grayscale, increase contrast, thresholding
    def upscale_amazon_image(url):
        return re.sub(r"_AC_.*?_", "_AC_SL1500_", url)
    
    from PIL import ImageEnhance, ImageOps
    def preprocess_for_ocr(pil_img):
        img = ImageOps.grayscale(pil_img)

        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        sharp = ImageEnhance.Sharpness(img)
        img = sharp.enhance(2.0)

        return img

    image_urls = extract_image_urls(soup)
    if not image_urls:
        print("No images found")
        return None

    images = []
    ocr_text = ""

    for url in image_urls:
        try:
            url = upscale_amazon_image(url)
            r = requests.get(url, timeout=10)
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img = preprocess_for_ocr(img)
            images.append(img)
            ocr_text += pytesseract.image_to_string(img, config = "--psm 11 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789%:-")
        except Exception:
            continue

    if images:
        pdf_path = os.path.join(output_dir, "product_images.pdf")
        images[0].save(pdf_path, save_all=True, append_images=images[1:])

    return ocr_text.strip()

def extract_html(link, product_name):
    driver = webdriver.Chrome()
    # go to link and search for product_name
    driver.get(link)
    time.sleep(3)
    search_box = driver.find_element(By.ID, "twotabsearchtextbox")
    search_box.clear()
    search_box.send_keys(product_name)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # open first result
    links = driver.find_elements(By.CSS_SELECTOR, "a.a-link-normal")

    product_link = None
    for link in links:
        href = link.get_attribute("href")
        if href and "/dp/" in href:
            product_link = link
            break

    product_link.click()

    def safe_text(soup, selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else None

    # parse product page
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    title = safe_text(soup, "#productTitle")
    price = safe_text(soup, ".a-price .a-offscreen")
    rating = safe_text(soup, "span.a-icon-alt")
    reviews_count = safe_text(soup, "#acrCustomerReviewText")
    df = pd.DataFrame([{
        "Title": title if title else None,
        "Price": price if price else None,
        "Rating": rating if rating else None,
        "Reviews Count": reviews_count if reviews_count else None
    }])
    return df, soup

def main():
    csv_file_path = str(sys.argv[1])
    link = str(sys.argv[2])

    csv_data = extract_csv(csv_file_path)
    product_name = csv_data['product_name'].iloc[0]
    web_data, soup = extract_html(link, product_name)
    pdf_data = extract_pdf(soup, "../data/pdf_output")

    for df in [csv_data, web_data]:
        print(df.head())

    print(f"Extracted PDF Text: {pdf_data}")

if __name__ == "__main__":
    main()