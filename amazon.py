import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1080")
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

base_url = 'https://partners.amazonaws.com'
search_url = f'{base_url}/search/partners/?offeringType=Consulting%20Service&page='

def create_driver():
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f"user-agent={user_agent}")
    return webdriver.Chrome(options=options)

def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))

def random_scroll(driver):
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    random_position = random.randint(0, scroll_height)
    driver.execute_script(f"window.scrollTo(0, {random_position});")
    random_delay(1, 2)

def get_company_details(card, driver):
    try:
        name_element = card.find('span', {'class': 'psf-partner-search-details-card__title'}).find('a')
        name = name_element.text if name_element else "No Name Found"
        link = base_url + name_element['href'] if name_element else "No Link Found"
        print(f"Parsed name: {name}, link: {link}")
    except AttributeError as e:
        print(f"Error parsing name or link: {e}")
        return None

    driver.get(link)
    random_delay(5, 7)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        website_element = soup.find('div', {'class': 'more-info__partner'}).find('a')
        website = website_element['href'] if website_element else "No Website Found"
        print(f"Parsed website: {website}")
    except AttributeError as e:
        print(f"Error parsing website: {e}")
        website = "No Website Found"

    return {'name': name, 'link': link, 'website': website}

def parse_page(page):
    driver = create_driver()
    random_delay(5, 7) 
    driver.get(search_url + str(page))
    random_delay(3, 5)

    random_scroll(driver)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.find_all('div', {'class': 'psf-partner-search-details-card__card'})

    companies = []

    if not cards:
        print(f"No cards found on page {page}.")
    else:
        for card in cards:
            details = get_company_details(card, driver)
            if details:
                companies.append(details)
                
    driver.quit()
    return companies

all_companies = []

for page in range(1, 131):
    companies = parse_page(page)
    all_companies.extend(companies)

df = pd.DataFrame(all_companies)
df.to_excel("companies.xlsx", index=False)

print("Data has been saved to companies.xlsx")
