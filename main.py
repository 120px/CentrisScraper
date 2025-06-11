import random
from datetime import date, datetime
import time
import json
from playwright.sync_api import sync_playwright

def main():
    start_timestamp = datetime.now().isoformat()
    start_time = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", headless=False)
        page = browser.new_page()

        # url = "https://www.centris.ca/en/properties~for-sale~griffintown-montreal-le-sud-ouest?uc=0"
        urls = ["https://www.centris.ca/en/properties~for-sale~griffintown-montreal-le-sud-ouest",
                "https://www.centris.ca/en/properties~for-sale~old-montreal-montreal-ville-marie"]

        for url in urls:
            area = url.split('~')[-1]
            print(f"Scraping area: {area}")
            load_listing_page(page, url)
            total_listings = int(show_total_listings(page))
            final_data = []

            for i in range(3):
                listing_data = extract_listing_data(page)
                print(listing_data)
                final_data.append(listing_data)
                navigate_to_next_listing(page)

            print(final_data)

            end_timestamp = datetime.now().isoformat()

            dt = datetime.fromisoformat(end_timestamp)
            # Get just the date part as a string
            date_str = dt.strftime("%Y-%m-%d")

            write_to_json(final_data, start_timestamp, end_timestamp, total_listings, filename=f"scraped_listings_{date_str}_{area}.json")
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

    print(f"\n📄 JSON data written to {filename}")



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
    total_listings = page.locator("#nav-results > div > div.d-none.d-lg-block.col-lg-4.align-self-end > p > span.js-resultCount.font-weight-bold").inner_text()
    print(total_listings)
    return total_listings

def navigate_to_next_listing(page):
    next_button = page.locator("#divWrapperPager > ul > li.next").first

    if next_button.is_visible():
        # Get some known element on the page to wait for it to disappear
        old_listing = page.locator(".property-thumbnail").first

        next_button.click(timeout=10000)

        # Wait for previous listing to be detached from DOM
        old_listing.wait_for(state="detached", timeout=10000)

    else:
        print("Next button not visible. Possibly last page.")

def extract_listing_data(page):
    listing_data = {}
    scrape_date = date.today().isoformat()
    try:
        page.wait_for_selector(".property-tagline", timeout=13000)

        page_url = page.url

        title = page.locator('#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 > h1 > span').inner_text()
        price = safe_text(page, ".price-container > .price")
        address = page.locator("#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 > div.d-flex.mt-1 > h2").inner_text()
        description_div = page.locator('div[itemprop="description"]')
        description_text = description_div.text_content()
        print(description_text.strip())

        features_data = extract_listing_features(page)
        listing_data["url"] = page_url
        listing_data["title"] = title
        listing_data["address"] = address
        listing_data["price"] = price
        listing_data["description"] = description_text
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

        print("🏠 Feature Info")
        print(f"Rooms: {rooms}")
        print(f"Bedrooms: {bedrooms}")
        print(f"Bathrooms: {bathrooms}")

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


# def scrape_listing_overview(page):
#     listings = page.locator("#divMainResult .property-thumbnail-item")
#     count = listings.count()
#     print(f"Found {count} listings.\n")
#
#     for i in range(count):
#         listing = listings.nth(i)
#         listing_data = open_listing_and_extract(page, listing)
#         final_data.append(listing_data)
#         return_to_listing_page(page)
#
# def open_listing_and_extract(page, listing):
#     try:
#         with page.expect_navigation(wait_until="load", timeout=15000):
#             link = listing.locator("a.property-thumbnail-summary-link")
#             link.click(timeout=5000)
#         return extract_listing_data(page)
#     except Exception as e:
#         print(f"Failed to open listing: {e}")

if __name__ == "__main__":
    main()