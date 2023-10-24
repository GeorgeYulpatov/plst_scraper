import os
import time
import re
import openpyxl
import requests
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

THREAD_COUNT = 5  


def setup_driver():
    user_agent = UserAgent()

    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={user_agent.random}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(options=options)


def download(urls):
    with FuturesSession(executor=ThreadPoolExecutor(max_workers=THREAD_COUNT)) as session:
        futures = [session.get(url) for url in urls]

        for future in futures:
            response = future.result()
            file_image_name = os.path.basename(response.url)
            with open(f'photo_plst/{file_image_name}', 'wb') as f:
                f.write(response.content)
            time.sleep(1)  
            yield file_image_name


def scraper(driver, link_to_the_product):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    brand = "PLST"

    # Получение SKU в переводе написан как номер позиции над фото с лево
    sku = re.search(r'\d+', soup.find("p", class_="fr-ec-caption fr-ec-caption--color-secondary fr-ec-text-align-left fr-ec-caption--standard fr-ec-text-transform-normal").text).group()
    # Получение всей строки с категориями
    breadcrumb = soup.find("ol", class_="fr-ec-breadcrumb-group")
    items = [item.text.strip() for item in breadcrumb.find_all("li")]
    str_category = "/".join(items)
    split_line = str_category.split("/")
    gender = split_line[1] if len(split_line) > 1 else "-"
    category_1 = split_line[2] if len(split_line) > 1 else "-"
    category_2 = split_line[3] if len(split_line) > 2 else "-"
    category_3 = split_line[4] if len(split_line) > 3 else "-"
    product_name = split_line[-1] if len(split_line) > 0 else "-"
    if category_2 == product_name and category_3 == "-":
        category_2 = "-"

    color = soup.find("label", class_="fr-ec-label fr-ec-label--color-primary-dark fr-ec-label--large "
                                      "fr-ec-text-align-left fr-ec-text-transform-normal "
                                      "fr-ec-chip-group__value").text.strip()
    only_color = color.split(" ")[1]

    product_review = soup.find("div", class_="fr-ec-accordion__content--large")
    product_text = product_review.get_text(separator="\n")
    product_text_br = product_review.get_text(separator="<br>")

    product_review_tag = soup.find("div", class_="fr-ec-accordion__content--large").decode_contents()

    product_info = product_review.find_next("div", class_="fr-ec-accordion__content--large")
    product_info_text = product_info.get_text(separator="\n")
    product_info_text_br = product_info.get_text(separator="<br>")

    product_info_tag = product_review.find_next("div", class_="fr-ec-accordion__content--large").decode_contents()

    content_block = soup.find("div", class_="fr-ec-media-gallery__preview-chip-container")
    img_tags = content_block.find_all('img')
    all_srcset_urls = []
    for img in img_tags:
        url_img = img.get("src")
        parsed_url = urlparse(url_img)
        new_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
        all_srcset_urls.append(new_url)

    dir_pic_name = list(download(all_srcset_urls))

    product_info = {
        "SKU": sku,
        "Product Name": product_name,
        "Product Link": link_to_the_product,
        "Category 1": category_1,
        "Category 2": category_2,
        "Category 3": category_3,
        "Color": color,
        "Only Color": only_color,
        "Brand": brand,
        "Gender": gender,
        "Product Review": product_text,
        "Product Info Text": product_info_text,
        "Product Review Tag": product_review_tag,
        "Product Info Text Tag": product_info_tag,
        "Product Review BR": product_text_br,
        "Product Info Text BR": product_info_text_br,
        "Image Names": ", ".join(dir_pic_name)
    }
    print(product_info)
    return product_info


def get_product_links(sheet, driver, workbook):
    with open('plst_entire_urls_men_outerwear.txt', 'r', encoding='utf-8') as file:
        urls = list(line.strip() for line in file)

    for url_product in urls:
        print(url_product)
        driver.get(url_product)
        page_title = driver.title
        if "PLST(プラステ)公式 |" in page_title:
            product_info = scraper(driver, url_product)
            sheet.append(tuple(product_info.values()))
            workbook.save('Product Information PLST men.xlsx')
        else:
            driver.refresh()
            time.sleep(3)
            product_info = scraper(driver, url_product)
            sheet.append(tuple(product_info.values()))
            workbook.save('Product Information PLST men.xlsx')

    driver.quit()

def create_workbook():
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    headers = [
        "SKU", "Product Name", "Product Link", "Category 1", "Category 2", "Category 3", "Color", "Only Color",
        "Brand", "Gender", "Product Review", "Product Info Text", "Product Review Tag",
        "Product Info Text Tag", "Product Review BR", "Product Info Text BR", "Image Names"
    ]

    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num).value = header

    return workbook, sheet


def main():
    with setup_driver() as driver:
        try:
            workbook, sheet = create_workbook()
            get_product_links(sheet, driver, workbook)
            file_name = "Product Information PLST men.xlsx"
            workbook.save(file_name)
            driver.quit()
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
