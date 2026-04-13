import argparse
import logging
import random
import time
from contextlib import contextmanager
from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://partners.amazonaws.com"
SEARCH_PATH = "/search/partners/?offeringType=Consulting%20Service&page="

logger = logging.getLogger(__name__)


def _build_options(user_agent: str) -> Options:
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1080")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-agent={user_agent}")
    return options


@contextmanager
def _create_driver():
    ua = UserAgent()
    options = _build_options(ua.random)
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        driver.quit()


def _random_delay(min_delay: float = 1, max_delay: float = 3) -> None:
    time.sleep(random.uniform(min_delay, max_delay))


def _random_scroll(driver: webdriver.Chrome) -> None:
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    random_position = random.randint(0, scroll_height)
    driver.execute_script(f"window.scrollTo(0, {random_position});")
    _random_delay(1, 2)


def _get_company_details(
    card: Tag, driver: webdriver.Chrome
) -> Optional[dict[str, str]]:
    try:
        title_span = card.find(
            "span", {"class": "psf-partner-search-details-card__title"}
        )
        name_element = title_span.find("a") if title_span else None
        if not name_element:
            logger.warning("No name element found in card, skipping")
            return None
        name = name_element.text
        link = BASE_URL + name_element["href"]
        logger.info("Parsed name: %s, link: %s", name, link)
    except (AttributeError, KeyError) as e:
        logger.error("Error parsing name or link: %s", e)
        return None

    driver.get(link)
    _random_delay(5, 7)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        more_info = soup.find("div", {"class": "more-info__partner"})
        website_element = more_info.find("a") if more_info else None
        website = website_element["href"] if website_element else "No Website Found"
        logger.info("Parsed website: %s", website)
    except (AttributeError, KeyError) as e:
        logger.error("Error parsing website: %s", e)
        website = "No Website Found"

    return {"name": name, "link": link, "website": website}


def parse_page(page: int) -> list[dict[str, str]]:
    search_url = f"{BASE_URL}{SEARCH_PATH}{page}"
    with _create_driver() as driver:
        _random_delay(5, 7)
        driver.get(search_url)
        _random_delay(3, 5)
        _random_scroll(driver)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.find_all(
            "div", {"class": "psf-partner-search-details-card__card"}
        )

        if not cards:
            logger.warning("No cards found on page %d.", page)
            return []

        companies = []
        for card in cards:
            details = _get_company_details(card, driver)
            if details:
                companies.append(details)
        return companies


def scrape(start_page: int = 1, end_page: int = 131, output: str = "companies.xlsx") -> None:
    all_companies: list[dict[str, str]] = []

    for page in range(start_page, end_page + 1):
        logger.info("Scraping page %d/%d", page, end_page)
        try:
            companies = parse_page(page)
            all_companies.extend(companies)
        except Exception:
            logger.exception("Failed to scrape page %d, skipping", page)

    df = pd.DataFrame(all_companies)
    df.to_excel(output, index=False)
    logger.info("Data has been saved to %s (%d companies)", output, len(all_companies))


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape AWS partner listings")
    parser.add_argument("--start-page", type=int, default=1, help="First page to scrape (default: 1)")
    parser.add_argument("--end-page", type=int, default=130, help="Last page to scrape (default: 130)")
    parser.add_argument("--output", default="companies.xlsx", help="Output file path (default: companies.xlsx)")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    scrape(start_page=args.start_page, end_page=args.end_page, output=args.output)


if __name__ == "__main__":
    main()
