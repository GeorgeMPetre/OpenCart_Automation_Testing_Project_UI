from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)


class BasePage:
    """Common Selenium helpers used by all page objects (waits, clicks, typing, and basic checks)."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # ---------------------------
    # Find / wait helpers
    # ---------------------------

    def find_element(self, locator):
        """Returns the element once it is visible."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_present(self, locator):
        """Returns the element once it exists in the DOM."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_clickable(self, locator):
        """Returns the element once it can be clicked."""
        return self.wait.until(EC.element_to_be_clickable(locator))

    def is_visible(self, locator):
        """Returns True if the element becomes visible within the wait timeout."""
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def get_elements_text(self, locator):
        """Returns a list of non-empty text values from a list of elements."""
        elements = self.driver.find_elements(*locator)
        return [el.text.strip() for el in elements if (el.text or "").strip()]

    # ---------------------------
    # Scroll / click helpers
    # ---------------------------

    def _scroll_into_view(self, target):
        """Scrolls the page to bring a locator or element into view."""
        element = self.find_present(target) if isinstance(target, tuple) else target
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'center'});",
            element,
        )

    def _scroll_and_click(self, locator):
        """Scrolls to an element and clicks it."""
        self.find_present(locator)
        self._scroll_into_view(locator)
        self._click_when_clickable(locator)

    def _safe_click(self, element, timeout: int = 10) -> None:
        """Clicks a WebElement with a small retry for stale/intercept issues."""
        wait = WebDriverWait(
            self.driver,
            timeout,
            ignored_exceptions=(StaleElementReferenceException,),
        )

        wait.until(lambda d: element.is_displayed() and element.is_enabled())
        ActionChains(self.driver).move_to_element(element).pause(0.05).perform()

        try:
            element.click()
        except ElementClickInterceptedException:
            ActionChains(self.driver).move_to_element(element).pause(0.1).click(element).perform()

    def _dismiss_overlays(self):
        """Tries to close dropdowns/overlays that can block clicks."""
        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            ActionChains(self.driver).move_by_offset(1, 1).click().perform()
        except Exception:
            pass

    def _click_when_clickable(self, locator):
        """Clicks an element once present. Uses JS click to avoid intercept issues."""
        self.find_present(locator)
        el = self.driver.find_element(*locator)
        self.driver.execute_script("arguments[0].click();", el)

    def _select_default_options(self):
        """Selects the first real option in all product option dropdowns."""
        select_elements = self.driver.find_elements(By.XPATH, "//select[contains(@id, 'input-option')]")
        for el in select_elements:
            sel = Select(el)
            if len(sel.options) > 1:
                sel.select_by_index(1)

    # ---------------------------
    # Form helpers
    # ---------------------------

    def enter_text(self, locator, text):
        """Clears the field and types the given value."""
        element = self.find_element(locator)
        self._scroll_into_view(element)
        element.clear()
        element.send_keys(text)

    def _type(self, locator, value, clear_first=False):
        """Types into a field. Can optionally clear first."""
        element = self.find_present(locator)
        if clear_first:
            element.clear()
        element.send_keys(value)

    def _toggle(self, locator):
        """Toggles a checkbox/radio using JS click."""
        element = self.find_present(locator)
        self._scroll_into_view(element)
        self.driver.execute_script("arguments[0].click();", element)

    # ---------------------------
    # Simple wrappers
    # ---------------------------

    def click(self, locator):
        """Simple click wrapper used by page objects."""
        self._click_when_clickable(locator)

    def get_text(self, locator):
        """Returns visible text from an element."""
        return self.find_element(locator).text.strip()

    def get_attribute(self, locator, attribute):
        """Returns an element attribute value."""
        return self.find_element(locator).get_attribute(attribute)
