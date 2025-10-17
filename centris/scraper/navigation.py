from utility.utilities import human_delay

def go_to_summary_view(page):
    button = page.wait_for_selector("#ButtonViewSummary")
    button.click()

def load_listing_page(page, url):
    page.goto(url, timeout=60000)

    try:
        cookie_accept = page.locator("#didomi-notice-agree-button")
        if cookie_accept.is_visible():
            cookie_accept.click()
    except:
        print("Cookie banner not found or already accepted.")


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

def navigate_to_next_listing(page):
    next_button = page.locator("#divWrapperPager > ul > li.next").first
    if next_button.is_visible():
        next_button.click(timeout=10000)
        human_delay(3, 9)

    else:
        print("Next button not visible. Possibly last page.")