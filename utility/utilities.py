import json
import random
import time

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


def human_delay(min_sec=2, max_sec=5):
    delay = random.uniform(min_sec, max_sec)
    print(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)


def safe_text(node, selector, default="N/A"):
    try:
        return node.locator(selector).inner_text(timeout=2000).strip()
    except:
        return default

def clean_price(price_str):
    """Convert a price string like '$1,495,000' to a float."""
    if not price_str:
        return 0.0
    cleaned = price_str.replace('$', '').replace(',', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0