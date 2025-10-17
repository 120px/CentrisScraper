import time
from datetime import date, datetime
from playwright.sync_api import sync_playwright
from database.database import Database
from centris.scraper.search import search_for_locations, set_filters
from centris.scraper.extractor import extract_listing_data, show_total_listings
from centris.scraper.navigation import sort_listings, navigate_to_next_listing, load_listing_page, go_to_summary_view

def main():
    db = Database()
    start_timestamp = datetime.now().isoformat()
    start_time = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        load_listing_page(page, "https://www.centris.ca/en")

        search_for_locations(page, locations=["montreal island"])
        page.click("#js-home-button-search-container")

        # set_filters(page)
        go_to_summary_view(page)
        sort_listings(page)

        total_listings = show_total_listings(page)
        final_data = []

        for i in range(1):
            listing_data = extract_listing_data(page)
            final_data.append(listing_data)
            navigate_to_next_listing(page)

        end_timestamp = datetime.now().isoformat()

        dt = datetime.fromisoformat(end_timestamp)
        # Get just the date part as a string
        date_str = dt.strftime("%Y-%m-%d")

        for listing in final_data:
            db.insert_listing(listing_data=listing)
            print(listing)

    browser.close()


def setup():
    return time.time()


def end(start_time):
    return time.time() - start_time


if __name__ == "__main__":
    main()
