from dataclasses import dataclass
from typing import Callable, Optional
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils.base_page import BasePage


@dataclass(frozen=True)
class Urls:
    """Keeps the key OpenCart URLs in one place."""
    base: str = "http://localhost/opencart/upload/index.php"


class NavigationPage(BasePage):
    """Handles the main OpenCart navigation: header links, categories, and account area pages."""

    urls = Urls()

    # ---------------------------
    # Generic
    # ---------------------------
    BODY = (By.CSS_SELECTOR, "body")
    CONTENT = (By.CSS_SELECTOR, "div#content")
    H1 = (By.TAG_NAME, "h1")

    # ---------------------------
    # Header / Currency
    # ---------------------------
    CURRENCY_TOGGLE = (By.XPATH, "//form[@id='form-currency']//a[@data-bs-toggle='dropdown']")
    CURRENCY_EURO = (
        By.XPATH,
        "//form[@id='form-currency']//a[contains(@class,'dropdown-item') and contains(., 'Euro')]",
    )
    PRICE_TEXT = (By.CSS_SELECTOR, ".price, .product-price, .product-thumb .price")

    # ---------------------------
    # Header / Quick links
    # ---------------------------
    WISHLIST_TOTAL = (By.ID, "wishlist-total")
    SHOPPING_CART = (By.XPATH, "//a[@title='Shopping Cart']")
    CHECKOUT = (By.XPATH, "//a[@title='Checkout']")
    LOGOUT = (By.LINK_TEXT, "Logout")
    MY_ACCOUNT = (By.CSS_SELECTOR, "a[href*='route=account/account']")
    LOGIN = (By.LINK_TEXT, "Login")
    # My Account dropdown toggle (default OC4)
    MY_ACCOUNT_TOGGLE = (By.XPATH, "//a[@data-bs-toggle='dropdown' and contains(., 'My Account')]")
    # Items inside the dropdown (works with/without token because it’s the actual href)
    MY_ACCOUNT_DROPDOWN_MY_ACCOUNT = (By.XPATH, "//a[contains(@href,'route=account/account')]")
    MY_ACCOUNT_DROPDOWN_LOGIN = (By.XPATH, "//a[contains(@href,'route=account/login')]")

    # ---------------------------
    # Category navigation
    # ---------------------------
    DESKTOPS = (By.LINK_TEXT, "Desktops")
    DESKTOPS_MAC = (By.PARTIAL_LINK_TEXT, "Mac")

    LAPTOPS_NOTEBOOKS = (By.LINK_TEXT, "Laptops & Notebooks")
    LAPTOPS_SHOW_ALL = (By.XPATH, "//a[@class='see-all' and contains(., 'Laptops')]")

    COMPONENTS = (By.LINK_TEXT, "Components")
    COMPONENTS_SHOW_ALL = (By.LINK_TEXT, "Show All Components")

    TABLETS = (By.LINK_TEXT, "Tablets")
    SOFTWARE = (By.LINK_TEXT, "Software")
    PHONES_PDAS = (By.LINK_TEXT, "Phones & PDAs")
    CAMERAS = (By.LINK_TEXT, "Cameras")
    MP3_PLAYERS = (By.LINK_TEXT, "MP3 Players")

    # ---------------------------
    # Account area links
    # ---------------------------
    # Marker can vary; keep it, but don’t rely only on it.
    ACCOUNT_MARKER = (By.ID, "account-account")

    EDIT_ACCOUNT = (By.LINK_TEXT, "Edit your account information")
    CHANGE_PASSWORD = (By.LINK_TEXT, "Change your password")
    ADDRESS_BOOK = (By.LINK_TEXT, "Modify your address book entries")
    ACCOUNT_WISHLIST = (By.LINK_TEXT, "Modify your wish list")

    PAYMENT_METHODS = (
        By.XPATH,
        "//a[normalize-space(.)='Payment Methods' or normalize-space(.)='Modify your payment methods']",
    )
    ORDER_HISTORY = (By.LINK_TEXT, "View your order history")
    SUBSCRIPTIONS = (
        By.XPATH,
        "//a[normalize-space(.)='Subscriptions' or normalize-space(.)='Recurring payments']",
    )
    REWARD_POINTS = (By.LINK_TEXT, "Your Reward Points")
    RETURN_REQUESTS = (By.LINK_TEXT, "View your return requests")
    TRANSACTIONS = (By.LINK_TEXT, "Your Transactions")

    DOWNLOADS_ON_ACCOUNT = (
        By.CSS_SELECTOR,
        "a[href*='route=account/download'][href*='customer_token']",
    )

    # ---------------------------
    # Messages
    # ---------------------------
    ALERT_SUCCESS = (By.CSS_SELECTOR, "div.alert-success")
    ALERT_DANGER = (By.CSS_SELECTOR, "div.alert-danger")
    EMPTY_CART_MESSAGE = (
        By.XPATH,
        "//div[@id='content']//p[contains(text(), 'Your shopping cart is empty')]",
    )

    # ---------------------------
    # Affiliate
    # ---------------------------
    AFFILIATE_LINK_ANYWHERE = (By.CSS_SELECTOR, "a[href*='route=account/affiliate']")
    AFFILIATE_LINK_TOKENIZED = (By.CSS_SELECTOR, "a[href*='route=account/affiliate'][href*='customer_token']")

    AFFILIATE_COMPANY = (By.CSS_SELECTOR, "input[name='company']")
    AFFILIATE_WEBSITE = (By.CSS_SELECTOR, "input[name='website']")
    AFFILIATE_TAX = (By.CSS_SELECTOR, "input[name='tax']")
    AFFILIATE_PAYMENT_CHEQUE = (By.XPATH, "//input[@type='radio' and @value='cheque']")
    AFFILIATE_CHEQUE_PAYEE = (By.CSS_SELECTOR, "input[name='cheque']")
    AFFILIATE_AGREE = (By.XPATH, "//input[@type='checkbox' and @name='agree']")
    CONTINUE = (
        By.XPATH,
        "//*[self::button or self::input][@type='submit' and "
        "(normalize-space(text())='Continue' or @value='Continue')]",
    )

    # ---------------------------
    # Newsletter
    # ---------------------------
    NEWSLETTER_SIDEBAR = (
        By.CSS_SELECTOR,
        "aside#column-right a.list-group-item[href*='route=account/newsletter']",
    )
    NEWSLETTER_IN_CONTENT = (By.CSS_SELECTOR, "#content a[href*='route=account/newsletter']")
    NEWSLETTER_CHECKBOX = (By.ID, "input-newsletter")

    # ---------------------------
    # Public navigation
    # ---------------------------
    def open_home(self) -> None:
        """Opens the home page and waits until the page is loaded."""
        self.driver.get(self.urls.base)
        self.wait.until(EC.presence_of_element_located(self.BODY))

    def ensure_home(self) -> None:
        """Opens home only if we are not already there."""
        if self.driver.current_url.rstrip("/") != self.urls.base.rstrip("/"):
            self.open_home()

    # ---------------------------
    # Account dashboard (FIXED)
    # ---------------------------
    def open_account_dashboard(self) -> None:
        """
        Opens the account dashboard via the UI (token-safe).
        This avoids direct GET to a URL that may require customer_token.
        """
        if self._on_account_dashboard():
            self._wait_for_content()
            return

        self.ensure_home()

        # Open dropdown and click "My Account"
        self._click_when_clickable(self.MY_ACCOUNT_TOGGLE)
        self.wait.until(EC.visibility_of_element_located(self.MY_ACCOUNT_DROPDOWN_MY_ACCOUNT))
        self._click_when_clickable(self.MY_ACCOUNT_DROPDOWN_MY_ACCOUNT)

        # Wait for dashboard to load (don’t depend on a single marker)
        self.wait.until(self._account_dashboard_loaded())
        self._wait_for_content()

    def _account_dashboard_loaded(self) -> Callable:
        """Wait predicate: account dashboard loaded OR redirected to login."""
        def _predicate(driver) -> bool:
            url = driver.current_url.lower()
            if "route=account/login" in url:
                return True
            # Marker if present
            if driver.find_elements(*self.ACCOUNT_MARKER):
                return True
            # Fallback: heading contains "My Account"
            h1s = driver.find_elements(*self.H1)
            if h1s and "my account" in (h1s[0].text or "").lower():
                return True
            return False

        return _predicate

    def _on_account_dashboard(self) -> bool:
        """True when already on the account dashboard."""
        url = self.driver.current_url.lower()
        if "route=account/account" in url:
            return True
        if self.driver.find_elements(*self.ACCOUNT_MARKER):
            return True
        return False

    # ---------------------------
    # Currency
    # ---------------------------
    def set_currency_euro(self) -> None:
        """Switches currency to Euro and waits until prices show the EUR symbol."""
        self._open_currency_dropdown()
        self._click_when_clickable(self.CURRENCY_EURO)
        self.wait.until(self._prices_contain("€"))

    def is_currency_euro(self) -> bool:
        """Returns True when at least one visible price shows the EUR symbol."""
        self.wait.until(EC.presence_of_all_elements_located(self.PRICE_TEXT))
        return any(e.is_displayed() and "€" in e.text for e in self.driver.find_elements(*self.PRICE_TEXT))

    def _open_currency_dropdown(self) -> None:
        """Opens the currency dropdown if it is not already open."""
        toggle = self.wait.until(EC.element_to_be_clickable(self.CURRENCY_TOGGLE))
        if toggle.get_attribute("aria-expanded") == "true":
            return
        self._click_when_clickable(self.CURRENCY_TOGGLE)
        self.wait.until(lambda d: toggle.get_attribute("aria-expanded") == "true")

    def _prices_contain(self, symbol: str) -> Callable:
        """Wait predicate: True when a visible price contains the given symbol."""
        def _predicate(driver) -> bool:
            try:
                elements = driver.find_elements(*self.PRICE_TEXT)
                return any(e.is_displayed() and symbol in e.text for e in elements)
            except StaleElementReferenceException:
                return False

        return _predicate

    # ---------------------------
    # Header / cart
    # ---------------------------
    def open_login_from_header(self) -> None:
        """Opens the login page from the My Account dropdown."""
        self.driver.find_element(*self.BODY).send_keys("\ue011")  # HOME key
        self._click_when_clickable(self.MY_ACCOUNT)
        self.wait.until(EC.visibility_of_element_located(self.LOGIN))
        self._click_when_clickable(self.LOGIN)
        self._wait_for_content()


    def open_wishlist(self) -> None:
        """Opens Wish List (redirects to login if user is not authenticated)."""
        self._click_when_clickable(self.WISHLIST_TOTAL)
        self.wait.until(lambda d: "route=account/wishlist" in d.current_url or "route=account/login" in d.current_url)

    def is_redirected_to_login(self) -> bool:
        """True when the current page is the login page."""
        return "route=account/login" in self.driver.current_url

    def open_cart(self) -> None:
        """Opens the cart page from the header."""
        self._click_when_clickable(self.SHOPPING_CART)
        self._wait_for_content()

    def open_checkout(self) -> None:
        """Opens checkout from the header and waits until checkout route is loaded."""
        self._click_when_clickable(self.CHECKOUT)
        self.wait.until(lambda d: "route=checkout" in d.current_url)
        self._wait_for_content()

    def is_empty_cart_message_visible(self) -> bool:
        """Returns True when the cart empty message is visible."""
        return any(
            e.is_displayed() and "your shopping cart is empty" in e.text.lower()
            for e in self.driver.find_elements(*self.EMPTY_CART_MESSAGE)
        )

    def is_content_visible(self) -> bool:
        """Simple check used by tests to confirm the page loaded."""
        return self.is_visible(self.CONTENT)

    # ---------------------------
    # Category navigation
    # ---------------------------
    def open_desktops_mac(self) -> None:
        """Opens the Desktops - Mac category."""
        self._click_when_clickable(self.DESKTOPS)
        self._click_when_clickable(self.DESKTOPS_MAC)
        self._wait_for_content()

    def open_laptops_and_notebooks(self) -> None:
        """Opens the Laptops & Notebooks listing page."""
        self._click_when_clickable(self.LAPTOPS_NOTEBOOKS)
        self._click_when_clickable(self.LAPTOPS_SHOW_ALL)
        self._wait_for_content()

    def open_components(self) -> None:
        """Opens the Components listing page."""
        self._click_when_clickable(self.COMPONENTS)
        self._click_when_clickable(self.COMPONENTS_SHOW_ALL)
        self._wait_for_content()

    def open_tablets(self) -> None:
        """Opens the Tablets category."""
        self._click_when_clickable(self.TABLETS)
        self._wait_for_content()

    def open_software(self) -> None:
        """Opens the Software category."""
        self._click_when_clickable(self.SOFTWARE)
        self._wait_for_content()

    def open_phones_and_pdas(self) -> None:
        """Opens the Phones & PDAs category."""
        self._click_when_clickable(self.PHONES_PDAS)
        self._wait_for_content()

    def open_cameras(self) -> None:
        """Opens the Cameras category."""
        self._click_when_clickable(self.CAMERAS)
        self._wait_for_content()

    def open_mp3_players(self) -> None:
        """Opens the MP3 Players category."""
        self._click_when_clickable(self.MP3_PLAYERS)
        self._wait_for_content()

    # ---------------------------
    # Account pages (generic pattern)
    # ---------------------------
    def open_edit_account(self) -> None:
        """Opens Edit Account from the account dashboard."""
        self._click_when_clickable(self.EDIT_ACCOUNT)
        self.wait.until(EC.visibility_of_element_located(self.H1))

    def on_edit_account(self) -> bool:
        """True when the Edit Account page heading is shown."""
        return self._heading_contains("My Account Information")

    def open_change_password(self) -> None:
        """Opens Change Password from the account dashboard."""
        self._click_when_clickable(self.CHANGE_PASSWORD)
        self.wait.until(EC.visibility_of_element_located(self.H1))

    def on_change_password(self) -> bool:
        """True when the Change Password page heading is shown."""
        return self._heading_contains("Change Password")

    def open_address_book(self) -> None:
        """Opens Address Book from the account dashboard."""
        self._click_when_clickable(self.ADDRESS_BOOK)
        self.wait.until(EC.visibility_of_element_located(self.H1))

    def on_address_book(self) -> bool:
        """True when the Address Book page heading is shown."""
        return self._heading_contains("Address Book")

    def open_account_wishlist(self) -> None:
        """Opens Wish List from the account dashboard."""
        self._click_when_clickable(self.ACCOUNT_WISHLIST)
        self.wait.until(EC.visibility_of_element_located(self.H1))

    def on_account_wishlist(self) -> bool:
        """True when the Wish List page heading is shown."""
        return self._heading_contains("wishlist", ignore_case=True)

    def open_payment_methods(self) -> None:
        """Opens Payment Methods from the account dashboard."""
        self._click_when_clickable(self.PAYMENT_METHODS)
        self.wait.until(EC.visibility_of_element_located(self.H1))

    def on_payment_methods(self) -> bool:
        """True when the Payment Methods page heading is shown."""
        return self._heading_contains("Payment Method")

    def open_order_history(self) -> None:
        """Opens Order History from the account dashboard."""
        self._click_when_clickable(self.ORDER_HISTORY)
        self.wait.until(EC.visibility_of_element_located(self.H1))

    def on_order_history(self) -> bool:
        """True when the Order History page heading is shown."""
        return self._heading_contains("Order History")

    def open_subscriptions(self) -> None:
        """Opens Subscriptions and waits until the page is loaded."""
        self._click_when_clickable(self.SUBSCRIPTIONS)
        self.wait.until(lambda d: self.subscriptions_visible())

    def subscriptions_visible(self) -> bool:
        """Checks the page text to confirm subscriptions/recurring content is present."""
        content = self.driver.find_elements(By.CSS_SELECTOR, "#content")
        if not content:
            return False
        text = content[0].text.lower()
        return "subscriptions" in text or "recurring payments" in text

    def open_downloads(self) -> None:
        """Opens Downloads using the tokenized link from the account page."""
        if "route=account/account" not in self.driver.current_url:
            self.open_account_dashboard()

        link = self.wait.until(EC.presence_of_element_located(self.DOWNLOADS_ON_ACCOUNT))
        self.driver.get(link.get_attribute("href"))
        self.wait.until(lambda d: "route=account/download" in d.current_url)
        self.wait.until(EC.presence_of_element_located((By.ID, "content")))

    def downloads_visible(self) -> bool:
        """Checks the Downloads page content is present."""
        if "route=account/download" not in self.driver.current_url:
            return False
        content = self.driver.find_elements(By.ID, "content")
        if not content:
            return False
        text = content[0].text.lower()
        return "download" in text or "downloads" in text or "no downloads" in text

    def open_reward_points(self) -> None:
        """Opens Reward Points from the account dashboard."""
        self._click_when_clickable(self.REWARD_POINTS)
        self.wait.until(EC.visibility_of_element_located(self.H1))

    def on_reward_points(self) -> bool:
        """True when Reward Points page is shown."""
        return self._heading_contains("Your Reward Points")

    def open_return_requests(self) -> None:
        """Opens Returns from the account dashboard."""
        self._click_when_clickable(self.RETURN_REQUESTS)
        self.wait.until(EC.visibility_of_element_located(self.H1))

    def on_return_requests(self) -> bool:
        """True when the Returns page is shown."""
        return self._heading_contains("Returns")

    def open_transactions(self) -> None:
        """Opens Transactions from the account dashboard."""
        self._click_when_clickable(self.TRANSACTIONS)
        self.wait.until(EC.visibility_of_element_located(self.H1))

    def on_transactions(self) -> bool:
        """True when the Transactions page is shown."""
        return self._heading_contains("Your Transactions")

    # ---------------------------
    # Affiliate
    # ---------------------------
    def open_affiliate(self) -> None:
        """Opens the Affiliate page from the account dashboard (token-safe)."""
        if self.on_affiliate_page():
            return

        if "route=account/account" not in self.driver.current_url:
            self.open_account_dashboard()

        link = None
        tokenized = self.driver.find_elements(*self.AFFILIATE_LINK_TOKENIZED)
        if tokenized:
            link = tokenized[0]
        else:
            any_link = self.driver.find_elements(*self.AFFILIATE_LINK_ANYWHERE)
            if any_link:
                link = any_link[0]

        if not link:
            raise AssertionError(
                "Affiliate link not found on Account page. "
                "Expected a link with href containing 'route=account/affiliate'."
            )

        self.driver.get(link.get_attribute("href"))
        self.wait.until(lambda d: "route=account/affiliate" in d.current_url)
        self._wait_for_content()

    def ensure_affiliate_profile(
        self,
        *,
        company: str,
        website: str,
        tax_id: str,
        payment_method: str,
        cheque_payee_name: Optional[str] = None,
    ) -> None:
        """Register if missing, otherwise edit."""
        self.open_affiliate()

        if self._affiliate_registration_required():
            self.register_affiliate(
                company=company,
                website=website,
                tax_id=tax_id,
                payment_method=payment_method,
                cheque_payee_name=cheque_payee_name,
            )
        else:
            self.edit_affiliate(
                company=company,
                website=website,
                tax_id=tax_id,
                payment_method=payment_method,
                cheque_payee_name=cheque_payee_name,
            )

    def register_affiliate(
        self,
        *,
        company: str,
        website: str,
        tax_id: str,
        payment_method: str,
        cheque_payee_name: Optional[str] = None,
    ) -> None:
        """Fills the affiliate form and submits it (registration state)."""
        self.open_affiliate()

        self._type(self.AFFILIATE_COMPANY, company)
        self._type(self.AFFILIATE_WEBSITE, website)
        self._type(self.AFFILIATE_TAX, tax_id)

        if (payment_method or "").strip().lower() == "cheque":
            self._toggle(self.AFFILIATE_PAYMENT_CHEQUE)
            if cheque_payee_name:
                self._type(self.AFFILIATE_CHEQUE_PAYEE, cheque_payee_name)

        agree = self.driver.find_elements(*self.AFFILIATE_AGREE)
        if agree and agree[0].is_displayed() and not agree[0].is_selected():
            self._toggle(self.AFFILIATE_AGREE)

        self._click_when_clickable(self.CONTINUE)
        self.wait.until(EC.visibility_of_element_located(self.ALERT_SUCCESS))

    def edit_affiliate(
        self,
        *,
        company: str,
        website: str,
        tax_id: str,
        payment_method: str,
        cheque_payee_name: Optional[str] = None,
    ) -> None:
        """Edits affiliate details and submits (already registered state)."""
        self.open_affiliate()

        self._type(self.AFFILIATE_COMPANY, company)
        self._type(self.AFFILIATE_WEBSITE, website)
        self._type(self.AFFILIATE_TAX, tax_id)

        if (payment_method or "").strip().lower() == "cheque":
            self._toggle(self.AFFILIATE_PAYMENT_CHEQUE)
            if cheque_payee_name:
                self._type(self.AFFILIATE_CHEQUE_PAYEE, cheque_payee_name)

        self._click_when_clickable(self.CONTINUE)
        self.wait.until(EC.visibility_of_element_located(self.ALERT_SUCCESS))

    def _affiliate_registration_required(self) -> bool:
        """True when affiliate registration is required."""
        agree = self.driver.find_elements(*self.AFFILIATE_AGREE)
        if agree and agree[0].is_displayed():
            return True

        company_fields = self.driver.find_elements(*self.AFFILIATE_COMPANY)
        if company_fields:
            current = (company_fields[0].get_attribute("value") or "").strip()
            return current == ""

        return False

    def affiliate_success(self) -> bool:
        """True when the affiliate update success message is shown."""
        return any(
            e.is_displayed() and "successfully updated" in e.text.lower()
            for e in self.driver.find_elements(*self.ALERT_SUCCESS)
        )

    def on_affiliate_page(self) -> bool:
        """True when the page heading shows Affiliate."""
        return self._heading_contains("Affiliate", ignore_case=True)

    # ---------------------------
    # Newsletter
    # ---------------------------
    def open_newsletter(self) -> None:
        """Opens the newsletter settings page from the account area."""
        if "route=account/account" not in self.driver.current_url:
            self.open_account_dashboard()

        sidebar = self.driver.find_elements(*self.NEWSLETTER_SIDEBAR)
        content = self.driver.find_elements(*self.NEWSLETTER_IN_CONTENT)
        link = sidebar[0] if sidebar else (content[0] if content else None)
        if not link:
            raise AssertionError("Newsletter link not found on Account page.")

        self.driver.get(link.get_attribute("href"))
        self.wait.until(lambda d: "route=account/newsletter" in d.current_url.lower())
        self.wait.until(EC.presence_of_element_located((By.ID, "content")))

    def set_newsletter(self, *, subscribe: bool = True) -> None:
        """Updates newsletter preference and waits for the success banner."""
        checkbox = self.driver.find_elements(*self.NEWSLETTER_CHECKBOX)
        if checkbox:
            box = checkbox[0]
            if subscribe != box.is_selected():
                self._toggle(self.NEWSLETTER_CHECKBOX)
        else:
            value = "1" if subscribe else "0"
            self._toggle((By.XPATH, f"//input[@type='radio' and @value='{value}']"))

        self._click_when_clickable(self.CONTINUE)
        self.wait.until(EC.visibility_of_element_located(self.ALERT_SUCCESS))

    def newsletter_success(self) -> bool:
        """True when the newsletter update success message is shown."""
        return any(
            e.is_displayed() and "newsletter subscription has been successfully updated" in e.text.lower()
            for e in self.driver.find_elements(*self.ALERT_SUCCESS)
        )

    # ---------------------------
    # Logout
    # ---------------------------
    def logout(self) -> None:
        """Logs out from the header and waits for the page to load."""
        self._click_when_clickable(self.LOGOUT)
        self.wait.until(EC.presence_of_element_located(self.BODY))

    def is_logged_out(self) -> bool:
        """Simple check that logout page is displayed."""
        return "account logout" in self.driver.page_source.lower()

    # ---------------------------
    # Internal helpers
    # ---------------------------
    def _wait_for_content(self) -> None:
        """Waits until main page content is visible."""
        self.wait.until(EC.visibility_of_element_located(self.CONTENT))

    def _heading_contains(self, expected: str, *, ignore_case: bool = False) -> bool:
        """Checks the first H1 contains the expected text."""
        headings = self.driver.find_elements(*self.H1)
        if not headings:
            return False
        actual = headings[0].text or ""
        if ignore_case:
            return expected.lower() in actual.lower()
        return expected in actual
