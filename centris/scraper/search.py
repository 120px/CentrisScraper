import time

from playwright.async_api import Page

from utility.utilities import human_delay

def search_for_locations(page, locations):
    search_box = page.locator("#js-property-search-bar input")

    for location in locations:
        search_box.fill(location)
        human_delay(1, 3)
        selection_box = page.locator(".select2-results__options")
        if selection_box.count() > 0:
            selection_box = page.locator(".select2-results__option").first
            selection_box.click()
        time.sleep(4)


def set_filters (page: Page):
    page.click("#filter-search")
    human_delay(1, 3)

    filter_form = page.locator("#secondary-search-form")
    filter_form.locator("#PropertyTypeSection-heading-filters").click()
    human_delay(1, 3)

    checkbox = page.locator("#PropertyType-SingleFamilyHome-input")
    checkbox.wait_for(state="attached", timeout=5000)
    checkbox.check(force=True)

    checkbox = page.locator("#PropertyType-SellCondo-input")
    checkbox.wait_for(state="attached", timeout=5000)
    checkbox.check(force=True)
