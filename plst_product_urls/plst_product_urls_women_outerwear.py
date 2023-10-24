import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    user_agent = UserAgent()

    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={user_agent.random}")
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(options=options)


def scraper(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    all_product_container = soup.find('div', class_="fr-ec-product-collection fr-ec-product-collection--type-grid-medium")
    link_product = all_product_container.find_all('a')

    urls = []
    for item in link_product:
        base_section_url = item.get("href")
        urls.append(base_section_url)

    urls = list(set(urls))

    with open('plst_urls_women_outerwear.txt', 'a') as file:
        for full_url in urls:
            file.write(f"https://www.plst.com{full_url}\n")


def get_product_links(driver):
    driver.get('https://www.plst.com/jp/ja/search?q=women&sort=1')

    for i in range(5):
        print(f"Scroll #: {i}")
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(10)

    scraper(driver)


def main():
    driver = setup_driver()
    get_product_links(driver)
    driver.quit()


if __name__ == "__main__":
    main()
