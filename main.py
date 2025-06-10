from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        # Launch Chromium in headless mode
        browser = p.chromium.launch(executable_path="C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                                    headless=False)
        page = browser.new_page()

        # Go to the Centris page
        url = "https://www.centris.ca/en/properties~for-sale~griffintown-montreal-le-sud-ouest?uc=0"
        page.goto(url, timeout=60000)

        cookie_accept = page.wait_for_selector("#didomi-notice-agree-button")
        if (cookie_accept != None):
            cookie_accept.click()

        page.wait_for_selector("#divMainResult")

        # Target the parent container
        main_div = page.locator("#divMainResult")

        listings = main_div.locator(".property-thumbnail-item")

        count = listings.count()
        print(f"Found {count} listings.\n")

        # Loop through and print some basic info
        for i in range(count):
            listing = listings.nth(i)
            description = listing.locator(".description").inner_text(timeout=2000)

            print(f"Listing {i + 1}:")
            print(f"Description: {description}")




        input()

if __name__ == "__main__":
    main()
