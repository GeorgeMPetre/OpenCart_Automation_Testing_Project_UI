from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from utils.base_page import BasePage


class CartPage(BasePage):
    """Handles the cart page: check items, change quantities, remove products, and start checkout."""

    CART_URL = "http://localhost/opencart/upload/index.php?route=checkout/cart&language=en-gb"

    CONTENT = (By.ID, "content")
    CART_TABLE = (By.CSS_SELECTOR, "#content table.table")
    CART_ROWS = (By.CSS_SELECTOR, "#content table.table tbody tr")
    EMPTY_CART_MESSAGE = (By.XPATH, "//*[@id='content']//p[contains(.,'Your shopping cart is empty')]")

    CHECKOUT_BUTTON = (By.LINK_TEXT, "Checkout")

    UPDATE_BUTTON = (
        By.XPATH,
        "//button[@type='submit' and contains(@formaction,'route=checkout/cart') and contains(@formaction,'edit')]",
    )

    GRAND_TOTAL_VALUE_CELL = (
        By.XPATH,
        "//*[@id='checkout-total']//tr[.//*[normalize-space()='Total']]/td[2]",
    )

    def __init__(self, driver):
        super().__init__(driver)

    # ---------------------------
    # Navigation
    # ---------------------------

    def navigate_to_cart(self) -> None:
        """Opens the cart page directly."""
        self.driver.get(self.CART_URL)
        self.wait_for_ready()

    # ---------------------------
    # Core waits
    # ---------------------------

    def wait_for_ready(self) -> bool:
        """Waits until the cart content is visible."""
        self.wait.until(EC.visibility_of_element_located(self.CONTENT))
        return True

    # ---------------------------
    # Row locators (dynamic)
    # ---------------------------

    def _row_locator_for_product(self, product_name: str):
        """Builds a locator for the cart row that contains the product link."""
        return (
            By.XPATH,
            f"//div[@id='content']//table[contains(@class,'table')]"
            f"//tr[.//a[normalize-space()='{product_name}']]",
        )

    def _remove_button_locator(self, product_name: str):
        """Builds a locator for the Remove button in a product row."""
        return (
            By.XPATH,
            f"//tr[.//a[normalize-space()='{product_name}']]"
            f"//button[contains(@formaction,'cart') and contains(@formaction,'remove')]",
        )

    def _qty_input_locator(self, product_name: str):
        """Builds a locator for the quantity input inside a product row."""
        return (
            By.XPATH,
            f"//a[normalize-space()='{product_name}']/ancestor::tr"
            f"//input[contains(@name,'quantity')]",
        )

    # ---------------------------
    # Cart checks
    # ---------------------------

    def is_product_in_cart(self, product_name: str) -> bool:
        """True when a product row exists in the cart."""
        self.wait_for_ready()
        return bool(self.driver.find_elements(*self._row_locator_for_product(product_name)))

    def is_cart_empty_message_displayed(self) -> bool:
        """True when the empty cart message is shown."""
        self.wait_for_ready()
        return bool(self.driver.find_elements(*self.EMPTY_CART_MESSAGE))

    def is_cart_layout_correct_when_empty(self) -> bool:
        """Basic UI check for empty cart state (content area visible)."""
        self.wait_for_ready()
        content = self.driver.find_elements(*self.CONTENT)
        return bool(content and content[0].is_displayed())

    # ---------------------------
    # Quantity
    # ---------------------------

    def get_product_quantity(self, product_name: str):
        """Returns the quantity for a product row as int, or None if not found."""
        self.wait_for_ready()
        els = self.driver.find_elements(*self._qty_input_locator(product_name))
        if not els:
            return None
        value = (els[0].get_attribute("value") or "").strip()
        return int(value) if value.isdigit() else None

    def wait_for_product_quantity(self, product_name: str, expected_qty: int, timeout: int = 8) -> None:
        """Waits until the cart shows the expected quantity for a product."""
        def _quantity_is_expected(_driver):
            qty = self.get_product_quantity(product_name)
            return qty == expected_qty

        WebDriverWait(self.driver, timeout).until(
            _quantity_is_expected,
            f"Expected quantity for {product_name} to be {expected_qty}",
        )

    def set_quantity(self, product_name: str, quantity: int) -> bool:
        """Types a new quantity value (does not click Update)."""
        self.wait_for_ready()
        qty_input = self.wait.until(EC.element_to_be_clickable(self._qty_input_locator(product_name)))
        self._scroll_into_view(qty_input)
        qty_input.clear()
        qty_input.send_keys(str(quantity))
        return True

    def update_cart(self) -> bool:
        """Clicks Update and waits for the cart to refresh."""
        self.wait_for_ready()
        self._click_when_clickable(self.UPDATE_BUTTON)
        self.wait_for_ready()
        return True

    def update_quantity(self, product_name: str, quantity: int) -> bool:
        """Changes quantity and applies the update."""
        self.set_quantity(product_name, quantity)
        self.update_cart()
        return True

    # ---------------------------
    # Remove product
    # ---------------------------

    def remove_product(self, product_name: str) -> bool:
        """Removes a product and waits until the row disappears or the cart becomes empty."""
        self.wait_for_ready()
        self._click_when_clickable(self._remove_button_locator(product_name))

        self.wait.until(
            lambda d: (len(d.find_elements(*self._row_locator_for_product(product_name))) == 0)
            or (len(d.find_elements(*self.EMPTY_CART_MESSAGE)) > 0)
        )
        self.wait_for_ready()
        return True

    # ---------------------------
    # Prices
    # ---------------------------

    def get_unit_price(self, product_name: str):
        """Returns unit price for the product row as float, or None."""
        self.wait_for_ready()
        rows = self.driver.find_elements(*self._row_locator_for_product(product_name))
        if not rows:
            return None
        cells = rows[0].find_elements(By.CSS_SELECTOR, "td.text-end")
        if not cells:
            return None
        return self._parse_price(cells[0].text)

    def get_total_price(self, product_name: str):
        """Returns total price for the product row as float, or None."""
        self.wait_for_ready()
        rows = self.driver.find_elements(*self._row_locator_for_product(product_name))
        if not rows:
            return None
        cells = rows[0].find_elements(By.CSS_SELECTOR, "td.text-end")
        if not cells:
            return None
        return self._parse_price((cells[-1].text or "").strip())

    def get_cart_grand_total(self):
        """Returns the cart grand total as float, or None."""
        self.wait_for_ready()
        cell = self.wait.until(EC.visibility_of_element_located(self.GRAND_TOTAL_VALUE_CELL))
        return self._parse_price(cell.text)

    def _parse_price(self, text: str):
        """Converts a price string like '£1,234.00' into a float."""
        clean = (text or "").replace("£", "").replace("$", "").replace(",", "").strip()
        return float(clean) if clean else None

    # ---------------------------
    # Checkout
    # ---------------------------

    def proceed_to_checkout(self) -> bool:
        """Clicks Checkout from the cart page."""
        self.wait_for_ready()
        self._click_when_clickable(self.CHECKOUT_BUTTON)
        return True
