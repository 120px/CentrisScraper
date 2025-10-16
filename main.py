import random
from datetime import date, datetime
import time
import json
from playwright.sync_api import sync_playwright
from database.database import Database


def main():
    db = Database()
    start_timestamp = datetime.now().isoformat()
    start_time = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        urls = ["https://www.centris.ca/en/properties~for-sale~griffintown-montreal-le-sud-ouest",
                "https://www.centris.ca/en/properties~for-sale~old-montreal-montreal-ville-marie"]

        for url in urls:
            area = url.split('~')[-1]
            load_listing_page(page, url)
            total_listings = int(show_total_listings(page))
            final_data = []

            # 3 is for testing purposes. Replace with total_listings
            for i in range(1):
                listing_data = extract_listing_data(page)
                final_data.append(listing_data)
                navigate_to_next_listing(page)

            end_timestamp = datetime.now().isoformat()

            dt = datetime.fromisoformat(end_timestamp)
            # Get just the date part as a string
            date_str = dt.strftime("%Y-%m-%d")

            for listing in final_data:
                db.insert_listing(listing_data=listing, site=area)
                print(listing)

            # write_to_json(final_data, start_timestamp, end_timestamp, total_listings, filename=f"scraped_listings_{date_str}_{area}.json")
            print(f"\n✅ Finished in {time.time() - start_time:.2f} seconds.")

    browser.close()


def setup():
    return time.time()


def end(start_time):
    return time.time() - start_time


def write_to_json(data, start, end, expected_count, filename="scraped_listings.json"):
    output = {
        "start_time": start,
        "end_time": end,
        "total_listings_expected": expected_count,
        "listings": data
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"\n JSON data written to {filename}")


def load_listing_page(page, url):
    page.goto(url, timeout=60000)

    try:
        cookie_accept = page.locator("#didomi-notice-agree-button")
        if cookie_accept.is_visible():
            cookie_accept.click()
    except:
        print("Cookie banner not found or already accepted.")

    go_to_summary_view(page)
    sort_listings(page)


def go_to_summary_view(page):
    button = page.wait_for_selector("#ButtonViewSummary")
    button.click()


def sort_listings(page):
    try:
        # Click the sort dropdown
        dropdown = page.locator("#dropdownSort")
        dropdown.click(timeout=5000)

        # Wait for the menu to appear
        dropdown_menu = page.locator("#selectSortById > div.dropdown-menu ")
        dropdown_menu.wait_for(timeout=5000)

        # Click on "Recent publications"
        option = dropdown_menu.locator('a.dropdown-item.option[data-option-value="3"]')
        option.click(timeout=5000)

        print("Sorted by Recent publications.")
    except Exception as e:
        print(f"Failed to sort listings: {e}")


def show_total_listings(page):
    total_listings = page.locator(
        "#nav-results > div > div.d-none.d-lg-block.col-lg-4.align-self-end > p > span.js-resultCount.font-weight-bold").inner_text()
    return total_listings


def navigate_to_next_listing(page):
    next_button = page.locator("#divWrapperPager > ul > li.next").first
    if next_button.is_visible():
        next_button.click(timeout=10000)
        human_delay(3, 9)

    else:
        print("Next button not visible. Possibly last page.")


def extract_listing_data(page):
    listing_data = {}
    scrape_date = date.today().isoformat()
    try:
        page.wait_for_selector(".property-tagline", timeout=13000)

        page_url = page.url

        title = page.locator(
            '#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 > h1 > span').inner_text()
        price = safe_text(page, ".price-container > .price")
        address = page.locator(
            "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 > div.d-flex.mt-1 > h2").inner_text()

        features_data = extract_listing_features(page)
        listing_data["url"] = page_url
        listing_data["title"] = title
        listing_data["address"] = address
        listing_data["price"] = price
        listing_data["region"] = address.split(",")[-1].strip()

        try:
            description_div = page.locator('div[itemprop="description"]')
            description_text = description_div.text_content(timeout=3000).strip()
            listing_data["description"] = description_text
        except:
            print("No description found for this listing.")
            listing_data["description"] = "N/A"

        listing_data["scrape_date"] = scrape_date
        listing_data.update(features_data)

        return listing_data

    except Exception as e:
        print(f"❌ Data extraction failed: {e}")


def extract_listing_features(page):
    feature_teaser_container = page.locator("div.row.teaser")
    features_data = {}
    # We expect only one "teaser" per listing page
    if feature_teaser_container.count() > 0:
        container = feature_teaser_container.nth(0)

        rooms = safe_text(container, ".piece")
        bedrooms = safe_text(container, ".cac")
        bathrooms = safe_text(container, ".sdb")

        features_data["rooms"] = rooms
        features_data["bedrooms"] = bedrooms
        features_data["bathrooms"] = bathrooms

        container = feature_teaser_container.nth(0)

        # Access the sibling of the feature_teaser_container
        sibling = container.locator("xpath=following-sibling::*[1]")
        if sibling.count() > 0:
            try:
                features_data["listing_id"] = sibling.locator("#ListingId").text_content().strip()
                features_data["prop_lat"] = sibling.locator("#PropertyLat").text_content().strip()
                features_data["prop_long"] = sibling.locator("#PropertyLng").text_content().strip()
            except Exception as e:
                print(f"Error extracting additional features: {e}")
                features_data["listing_id"] = "N/A"
                features_data["prop_lat"] = "N/A"
                features_data["prop_long"] = "N/A"

        return features_data
    else:
        print("No teaser section found.")


def safe_text(node, selector, default="N/A"):
    try:
        return node.locator(selector).inner_text(timeout=2000).strip()
    except:
        return default


def human_delay(min_sec=2, max_sec=5):
    delay = random.uniform(min_sec, max_sec)
    print(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)


if __name__ == "__main__":
    main()
