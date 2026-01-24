from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from utils.base_page import BasePage


class ProductPage(BasePage):
    """Works with product pages: open a product, set quantity, pick options, and add to cart.
    """

    # ---------------------------
    # Locators (Product listing / selection)
    # ---------------------------
    PRODUCT_BY_NAME_XPATH = (
        "//div[contains(@class,'product-thumb')]//a[normalize-space(text())='{name}']"
    )

    # ---------------------------
    # Locators (Product details)
    # ---------------------------
    QUANTITY_INPUT = (By.ID, "input-quantity")
    ADD_TO_CART_BUTTON = (By.ID, "button-cart")
    SUCCESS_ALERT = (By.CSS_SELECTOR, ".alert-success")

    OPTION_SELECTS = (By.XPATH, "//select[contains(@id, 'input-option')]")
    FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")

    def __init__(self, driver):
        super().__init__(driver)

    # ---------------------------
    # Navigation / selection
    # ---------------------------

    def open_product_from_list(self, product_name: str) -> None:
        """Opens a product from a listing page by clicking its name."""
        locator = (By.XPATH, self.PRODUCT_BY_NAME_XPATH.format(name=product_name))
        product = self.wait.until(EC.element_to_be_clickable(locator))
        self._scroll_into_view(product)
        self._safe_click(product)

    def select_product(self, product_name: str) -> None:
        """Selects a product from the product listing by name."""
        self.open_product_from_list(product_name)

    def select_required_dropdown_options(self) -> None:
        """Selects the first real value for each option dropdown (skips 'Please Select')."""
        selects = self.driver.find_elements(*self.OPTION_SELECTS)
        for el in selects:
            sel = Select(el)
            if len(sel.options) > 1:
                self._scroll_into_view(el)
                sel.select_by_index(1)

    # ---------------------------
    # Quantity
    # ---------------------------

    def set_quantity(self, quantity: int) -> None:
        """Sets the product quantity on the page."""
        field = self.wait.until(EC.element_to_be_clickable(self.QUANTITY_INPUT))
        self._scroll_into_view(field)
        field.clear()
        field.send_keys(str(quantity))

    # ---------------------------
    # Add to cart
    # ---------------------------

    def click_add_to_cart(self) -> None:
        """Clicks Add to Cart and waits for the success banner."""
        add_button = self.wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BUTTON))
        self._scroll_into_view(add_button)
        self._safe_click(add_button)
        self.wait.until(EC.visibility_of_element_located(self.SUCCESS_ALERT))

    def add_to_cart(self, quantity: int = 1) -> None:
        """Sets quantity and adds the product to the cart (does not touch options)."""
        self.set_quantity(quantity)
        self.click_add_to_cart()

    def is_add_to_cart_success_message_displayed(self) -> bool:
        """True when the success banner confirms the product was added."""
        alerts = self.driver.find_elements(*self.SUCCESS_ALERT)
        if not alerts:
            return False
        text = alerts[0].text or ""
        return ("Success: You have added" in text) and ("to your shopping cart!" in text)

    # ---------------------------
    # Options: generic defaults
    # ---------------------------

    def select_first_dropdown_options(self) -> None:
        """Selects index 1 for all option dropdowns (skips 'Please Select')."""
        selects = self.driver.find_elements(*self.OPTION_SELECTS)
        for el in selects:
            sel = Select(el)
            if len(sel.options) > 1:
                self._scroll_into_view(el)
                sel.select_by_index(1)

    # ---------------------------
    # Options: modular fillers
    # ---------------------------

    def choose_radio_value(self, value: str) -> None:
        """Selects a radio option by value."""
        locator = (By.XPATH, f"//input[@type='radio' and @value='{value}']")
        self._click_when_clickable(locator)

    def choose_checkbox_value(self, value: str) -> None:
        """Toggles a checkbox option by value."""
        locator = (By.XPATH, f"//input[@type='checkbox' and @value='{value}']")
        self._toggle(locator)

    def fill_text_option(self, name: str, text: str) -> None:
        """Fills a text option input by its name attribute."""
        locator = (By.NAME, name)
        self._type(locator, text)

    def fill_textarea_option(self, name: str, text: str) -> None:
        """Fills a textarea option by its name attribute."""
        locator = (By.NAME, name)
        self._type(locator, text)

    def fill_select_option(self, name: str, index: int = 1) -> None:
        """Selects an option dropdown by name and index."""
        locator = (By.NAME, name)
        el = self.wait.until(EC.presence_of_element_located(locator))
        self._scroll_into_view(el)
        Select(el).select_by_index(index)

    def fill_date_option(self, name: str, yyyy_mm_dd: str) -> None:
        """Fills a date input (yyyy-mm-dd)."""
        locator = (By.NAME, name)
        self._type(locator, yyyy_mm_dd, clear_first=True)

    def fill_time_option(self, name: str, hh_mm: str) -> None:
        """Fills a time input (hh:mm)."""
        locator = (By.NAME, name)
        self._type(locator, hh_mm, clear_first=True)

    def fill_datetime_option(self, name: str, value: str, tab_out: bool = True) -> None:
        """Fills a datetime input and optionally tabs out to trigger validation."""
        locator = (By.NAME, name)
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self._scroll_into_view(el)
        el.clear()
        el.send_keys(value)
        if tab_out:
            el.send_keys(Keys.TAB)

    def upload_file_option(self, button_id: str, file_path: str) -> None:
        """Uploads a file using the product upload button and accepts the result alert."""
        upload_btn = self.wait.until(EC.element_to_be_clickable((By.ID, button_id)))
        self._scroll_into_view(upload_btn)

        self.driver.execute_script("arguments[0].click();", upload_btn)

        file_input = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        file_input.send_keys(file_path)

        alert = self.wait.until(EC.alert_is_present())
        alert.accept()

    # ---------------------------
    # Scenario helper
    # ---------------------------

    def fill_default_options(self, upload_file_path: str) -> None:
        """Fills a known set of required options used by products like Apple Cinema 30\"."""
        self.choose_radio_value("5")
        self.choose_checkbox_value("8")
        self.fill_text_option("option[208]", "Test text")
        self.fill_textarea_option("option[209]", "Some longer text")
        self.fill_select_option("option[217]", index=1)
        self.upload_file_option("button-upload-222", upload_file_path)
        self.fill_date_option("option[219]", "2011-02-20")
        self.fill_datetime_option("option[220]", "2011-02-20T22:25:00")
        self.fill_time_option("option[221]", "22:25")
