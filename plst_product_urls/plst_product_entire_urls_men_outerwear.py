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


def following_a_link(driver):
    with open('plst_urls_men_outerwear.txt', mode='r', encoding='utf-8') as file:
        for url_product in file:
            url_product = url_product.strip()

            driver.get(url_product)
            time.sleep(random.uniform(3, 5))

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            code_product_container = soup.find('div', class_="fr-ec-chip-group__chips")
            link_product = code_product_container.find_all('input')

            urls = []
            for item in link_product:
                link_code = item.get("value")
                entire_url = f"{url_product}" + "?colorDisplayCode=" + f"{link_code}" + "&sizeDisplayCode=005"
                print(entire_url)
                urls.append(entire_url)
            urls = list(set(urls))

            with open('plst_entire_urls_men_outerwear.txt', 'a') as file:
                for full_url in urls:
                    file.write(f"{full_url}\n")
        driver.close()


def main():
    driver = setup_driver()
    following_a_link(driver)
    driver.quit()


if __name__ == "__main__":
    main()
