import pytest
import allure

@pytest.mark.sanity
@allure.feature('Sample Test')
def test_first_google_search(page):
    page.goto("https://www.google.com")

@pytest.mark.sanity
@allure.feature('Sample Test')
def test_second_google_search(page):
    page.goto("https://www.gmail.com")
    page.fill("input[name=q]", "Playwright")
    page.press("input[name=q]", "Enter")
    page.wait_for_selector("#search")
    assert "Playwright" in page.title()

@pytest.mark.sanity
@allure.feature('Sample Test')
def test_third_google_search(page):
    page.goto("https://www.gmail.com")
    page.fill("input[name=q]", "Playwright")
    page.press("input[name=q]", "Enter")
    page.wait_for_selector("#search")
    assert "Playwright" in page.title()
