import datetime
from utility.utilities import safe_text, clean_price
from urllib.parse import urlparse
from datetime import date

def show_total_listings(page):
    total_listings = page.locator(".js-resultCount").first.inner_text()
    return total_listings

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
        listing_data["price"] = clean_price(price)
        listing_data["region"] = address.split(",")[-1].strip()
        listing_data["site"] = urlparse(page_url).netloc.split('.')[-2]

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