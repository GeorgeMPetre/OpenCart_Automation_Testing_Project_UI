from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from utils.base_page import BasePage


class CheckoutPage(BasePage):
    """Runs the checkout steps end-to-end so tests only call one clean flow method."""

    # Shipping address
    SHIPPING_NEW_RADIO = (By.ID, "input-shipping-new")
    SHIPPING_NEW_SECTION = (By.ID, "shipping-new")

    SHIPPING_FIRSTNAME = (By.ID, "input-shipping-firstname")
    SHIPPING_LASTNAME = (By.ID, "input-shipping-lastname")
    SHIPPING_ADDRESS_1 = (By.ID, "input-shipping-address-1")
    SHIPPING_CITY = (By.ID, "input-shipping-city")
    SHIPPING_POSTCODE = (By.ID, "input-shipping-postcode")
    SHIPPING_COUNTRY = (By.ID, "input-shipping-country")
    SHIPPING_ZONE = (By.ID, "input-shipping-zone")

    SHIPPING_ADDRESS_CONTINUE = (By.ID, "button-shipping-address")

    # Shipping / Payment methods
    SHIPPING_METHOD_SELECT = (By.ID, "input-shipping-method")
    SHIPPING_METHOD_REFRESH = (By.ID, "button-shipping-method")

    PAYMENT_METHOD_SELECT = (By.ID, "input-payment-method")
    PAYMENT_METHOD_REFRESH = (By.ID, "button-payment-method")

    AGREE_CHECKBOX = (By.ID, "input-agree")

    ALERT_DANGER = (By.CSS_SELECTOR, "#alert .alert-danger")

    CONFIRM_BUTTON = (By.CSS_SELECTOR, "#checkout-payment button.btn-primary")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "#content h1")

    # ---------------------------
    # High-level flow
    # ---------------------------

    def complete_new_address_checkout_flow(
        self,
        firstname: str = "John",
        lastname: str = "Doe",
        address_1: str = "123 Testing Street",
        city: str = "Testville",
        postcode: str = "CT1 2AB",
        country: str = "United Kingdom",
        zone: str = "Kent",
        require_agree: bool = False,
    ) -> None:
        """Completes checkout using a new shipping address and places the order."""
        self.select_new_shipping_address()
        self.fill_new_shipping_address(
            firstname=firstname,
            lastname=lastname,
            address_1=address_1,
            city=city,
            postcode=postcode,
            country=country,
            zone=zone,
        )
        self.submit_new_shipping_address()

        self.refresh_and_select_shipping_method()
        self.refresh_and_select_payment_method()

        if require_agree:
            self.agree_if_present()

        self.confirm_order()

    def is_order_successful(self) -> bool:
        """True when the success page confirms the order was placed."""
        if not self.is_visible(self.SUCCESS_MESSAGE):
            return False
        text = (self.get_text(self.SUCCESS_MESSAGE) or "").lower()
        return "your order has been placed" in text

    # ---------------------------
    # Shipping address
    # ---------------------------

    def select_new_shipping_address(self) -> None:
        """Switches to 'new address' when the option exists, otherwise leaves default."""
        if not self.driver.find_elements(*self.SHIPPING_NEW_RADIO):
            return

        radio = self.wait.until(EC.presence_of_element_located(self.SHIPPING_NEW_RADIO))
        if not radio.is_selected():
            self.wait.until(EC.element_to_be_clickable(self.SHIPPING_NEW_RADIO)).click()

        self.wait.until(EC.visibility_of_element_located(self.SHIPPING_NEW_SECTION))

    def fill_new_shipping_address(
        self,
        firstname: str,
        lastname: str,
        address_1: str,
        city: str,
        postcode: str,
        country: str,
        zone: str,
    ) -> None:
        """Fills the shipping address form fields."""
        self._type(self.SHIPPING_FIRSTNAME, firstname)
        self._type(self.SHIPPING_LASTNAME, lastname)
        self._type(self.SHIPPING_ADDRESS_1, address_1)
        self._type(self.SHIPPING_CITY, city)
        self._type(self.SHIPPING_POSTCODE, postcode)

        self.select_by_text(self.SHIPPING_COUNTRY, country)

        zone_el = self.wait.until(EC.element_to_be_clickable(self.SHIPPING_ZONE))
        self._scroll_into_view(zone_el)
        self.select_by_text(self.SHIPPING_ZONE, zone)

    def submit_new_shipping_address(self) -> None:
        """Submits the shipping address step and waits for the next section to be ready."""
        btn = self.wait.until(EC.element_to_be_clickable(self.SHIPPING_ADDRESS_CONTINUE))
        self._scroll_into_view(btn)
        btn.click()

        self.wait.until(EC.presence_of_element_located(self.SHIPPING_METHOD_REFRESH))

    # ---------------------------
    # Shipping / Payment methods
    # ---------------------------

    def _wait_for_enabled_select_option(self, select_locator, timeout: int = 10) -> None:
        """Waits until the dropdown has at least one enabled option with a real value."""
        def _has_enabled_option(driver) -> bool:
            try:
                select_el = driver.find_element(*select_locator)
                options = Select(select_el).options
                return any(
                    (opt.get_attribute("value") or "").strip() and opt.is_enabled()
                    for opt in options
                )
            except StaleElementReferenceException:
                return False

        WebDriverWait(self.driver, timeout).until(_has_enabled_option)

    def _select_first_enabled_option(self, select_locator, retries: int = 3) -> None:
        """Selects the first enabled option that has a real value."""
        last_error = None

        for _ in range(retries):
            try:
                select_el = self.driver.find_element(*select_locator)
                sel = Select(select_el)

                for index, opt in enumerate(sel.options):
                    if (opt.get_attribute("value") or "").strip() and opt.is_enabled():
                        fresh_select = self.driver.find_element(*select_locator)
                        Select(fresh_select).select_by_index(index)
                        return

                raise AssertionError("No enabled selectable options found.")

            except StaleElementReferenceException as e:
                last_error = e

        raise AssertionError(f"Select became stale while selecting an option: {select_locator}") from last_error

    def refresh_and_select_shipping_method(self) -> None:
        """Refreshes shipping methods, selects the first valid one, then waits for payment step."""
        self._click_when_clickable(self.SHIPPING_METHOD_REFRESH)

        select_el = self.wait.until(EC.presence_of_element_located(self.SHIPPING_METHOD_SELECT))
        self._scroll_into_view(select_el)

        self._wait_for_enabled_select_option(self.SHIPPING_METHOD_SELECT)
        self._select_first_enabled_option(self.SHIPPING_METHOD_SELECT)

        self.wait.until(EC.presence_of_element_located(self.PAYMENT_METHOD_REFRESH))

    def refresh_and_select_payment_method(self) -> None:
        """Refreshes payment methods, selects the first valid one, then waits for confirm button."""
        self._click_when_clickable(self.PAYMENT_METHOD_REFRESH)

        if self.has_no_payment_methods_alert():
            raise AssertionError("No payment methods configured in store.")

        select_el = self.wait.until(EC.presence_of_element_located(self.PAYMENT_METHOD_SELECT))
        self._scroll_into_view(select_el)

        self._wait_for_enabled_select_option(self.PAYMENT_METHOD_SELECT)
        self._select_first_enabled_option(self.PAYMENT_METHOD_SELECT)

        self.wait.until(EC.element_to_be_clickable(self.CONFIRM_BUTTON))

    def has_no_payment_methods_alert(self) -> bool:
        """True when OpenCart shows 'no payment method available'."""
        alerts = self.driver.find_elements(*self.ALERT_DANGER)
        return any("no payment method available" in (a.text or "").lower() for a in alerts)

    def agree_if_present(self) -> None:
        """Ticks the terms checkbox if OpenCart shows it."""
        els = self.driver.find_elements(*self.AGREE_CHECKBOX)
        if not els:
            return

        cb = els[0]
        if not cb.is_selected():
            self._scroll_into_view(cb)
            cb.click()

    # ---------------------------
    # Confirm
    # ---------------------------

    def confirm_order(self) -> None:
        """Clicks Confirm Order and leaves the browser on the success page when it works."""
        self._dismiss_overlays()

        wait = WebDriverWait(self.driver, 15)
        btn = wait.until(EC.element_to_be_clickable(self.CONFIRM_BUTTON))

        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(self.driver).move_to_element(btn).perform()

        wait.until(lambda d: d.find_element(*self.CONFIRM_BUTTON).is_enabled())
        self.driver.find_element(*self.CONFIRM_BUTTON).click()

    # ---------------------------
    # Small helpers
    # ---------------------------

    def select_by_text(self, locator, text: str) -> None:
        """Selects a dropdown option by visible text."""
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self._scroll_into_view(el)
        Select(el).select_by_visible_text(text)

    def select_first_option(self, select_el) -> None:
        """Selects the first real dropdown option (index 1)."""
        sel = Select(select_el)
        if len(sel.options) <= 1:
            raise AssertionError("No selectable options in dropdown.")
        sel.select_by_index(1)
