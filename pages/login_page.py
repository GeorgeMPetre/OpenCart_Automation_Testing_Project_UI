from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from utils.base_page import BasePage


class LoginPage(BasePage):
    """Handles the OpenCart login page: open it, log in, and read login status/errors."""

    URL = "http://localhost/opencart/upload/index.php?route=account/login&language=en-gb"

    # Locators
    EMAIL_INPUT = (By.ID, "input-email")
    PASSWORD_INPUT = (By.ID, "input-password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']")
    ALERT_MESSAGE = (By.CSS_SELECTOR, "div.alert.alert-danger")

    # ---------------------------
    # Navigation
    # ---------------------------

    def open(self) -> "LoginPage":
        """Opens the login page and waits until the form is ready."""
        self.driver.get(self.URL)
        self.wait.until(EC.visibility_of_element_located(self.EMAIL_INPUT))
        return self

    def open_while_logged_in(self) -> "LoginPage":
        """Opens login while authenticated and waits for either login or account page."""
        self.driver.get(self.URL)
        self.wait.until(
            lambda d: "route=account/account" in d.current_url or "route=account/login" in d.current_url
        )
        return self

    # ---------------------------
    # Actions
    # ---------------------------

    def fill_email(self, email: str) -> "LoginPage":
        """Types email into the email field (trimmed)."""
        self.enter_text(self.EMAIL_INPUT, (email or "").strip())
        return self

    def fill_password(self, password: str) -> "LoginPage":
        """Types password into the password field (trimmed)."""
        self.enter_text(self.PASSWORD_INPUT, (password or "").strip())
        return self

    def submit(self) -> "LoginPage":
        """Clicks the Login button."""
        self._click_when_clickable(self.LOGIN_BUTTON)
        return self

    def submit_with_enter(self) -> "LoginPage":
        """Submits the form by pressing Enter in the password field."""
        password_field = self.wait.until(EC.visibility_of_element_located(self.PASSWORD_INPUT))
        password_field.send_keys(Keys.ENTER)
        return self

    def login(self, email: str, password: str, *, submit_via_enter: bool = True) -> "LoginPage":
        """Fills email/password and submits the form."""
        self.fill_email(email)
        self.fill_password(password)
        return self.submit_with_enter() if submit_via_enter else self.submit()

    # ---------------------------
    # State helpers
    # ---------------------------

    def wait_for_error_alert(self) -> "LoginPage":
        """Waits until the warning alert is visible."""
        self.wait.until(EC.visibility_of_element_located(self.ALERT_MESSAGE))
        return self

    def is_on_login_page(self) -> bool:
        """True when the current URL is the login route."""
        return "route=account/login" in self.driver.current_url

    def is_on_account_dashboard(self) -> bool:
        """True when the current URL is the account dashboard route."""
        return "route=account/account" in self.driver.current_url

    def wait_for_dashboard(self) -> bool:
        """Returns True if the account dashboard is reached within the wait time."""
        try:
            self.wait.until(EC.url_contains("route=account/account"))
            return True
        except Exception:
            return False

    def get_error_message(self) -> str:
        """Returns the alert message text if present, otherwise an empty string."""
        if self.is_visible(self.ALERT_MESSAGE):
            return self.get_text(self.ALERT_MESSAGE).strip()
        return ""

    def is_account_locked(self) -> bool:
        """Returns True when the error text suggests the account is locked or rate-limited."""
        message = self.get_error_message().lower()
        keywords = ("locked", "too many attempts", "captcha")
        return any(k in message for k in keywords)
