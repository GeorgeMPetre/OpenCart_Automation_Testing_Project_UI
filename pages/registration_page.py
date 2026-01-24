from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from utils.base_page import BasePage


class RegistrationPage(BasePage):
    """Handles the OpenCart registration page: open it, fill the form, submit, and read errors."""

    # ---------------------------
    # URL
    # ---------------------------
    REGISTER_URL = "http://localhost/opencart/upload/index.php?route=account/register&language=en-gb"

    # ---------------------------
    # Locators
    # ---------------------------
    FIRST_NAME_INPUT = (By.ID, "input-firstname")
    LAST_NAME_INPUT = (By.ID, "input-lastname")
    EMAIL_INPUT = (By.ID, "input-email")
    PASSWORD_INPUT = (By.ID, "input-password")

    PRIVACY_POLICY_CHECKBOX = (By.CSS_SELECTOR, "input[name='agree'][type='checkbox']")
    CONTINUE_BUTTON = (By.XPATH, "//button[normalize-space()='Continue']")

    GLOBAL_WARNING = (By.CSS_SELECTOR, ".alert-danger")
    FIELD_ERRORS = (By.CSS_SELECTOR, ".text-danger")

    ERROR_FIRSTNAME = (By.ID, "error-firstname")
    ERROR_LASTNAME = (By.ID, "error-lastname")
    ERROR_EMAIL = (By.ID, "error-email")
    ERROR_PASSWORD = (By.ID, "error-password")

    # Useful for redirect detection / page readiness checks
    BREADCRUMB = (By.CSS_SELECTOR, "ol.breadcrumb")
    CONTENT_H1 = (By.CSS_SELECTOR, "#content h1")

    # ---------------------------
    # Navigation
    # ---------------------------

    def open(self) -> "RegistrationPage":
        """Opens the registration page and waits until the page (or a redirect) settles."""
        self.driver.get(self.REGISTER_URL)

        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        self.wait.until(
            lambda d: (
                d.find_elements(*self.FIRST_NAME_INPUT)
                or "route=account/register" not in d.current_url
                or d.find_elements(*self.GLOBAL_WARNING)
            )
        )
        return self

    def navigate_to_registration(self) -> None:
        """Navigates to the registration page via direct URL."""
        self.open()

    def is_on_register_page(self) -> bool:
        """True when the current URL is still the registration route."""
        return "route=account/register" in self.driver.current_url

    # ---------------------------
    # Actions
    # ---------------------------

    def enter_first_name(self, first_name: str) -> None:
        """Types into the First Name field."""
        self.enter_text(self.FIRST_NAME_INPUT, first_name)

    def enter_last_name(self, last_name: str) -> None:
        """Types into the Last Name field."""
        self.enter_text(self.LAST_NAME_INPUT, last_name)

    def enter_email(self, email: str) -> None:
        """Types into the Email field."""
        self.enter_text(self.EMAIL_INPUT, email)

    def enter_password(self, password: str) -> None:
        """Types into the Password field."""
        self.enter_text(self.PASSWORD_INPUT, password)

    def set_privacy_policy(self, accept: bool = True) -> None:
        """Checks or unchecks the Privacy Policy box."""
        checkbox = self.wait.until(EC.presence_of_element_located(self.PRIVACY_POLICY_CHECKBOX))
        _ = checkbox.location_once_scrolled_into_view

        should_toggle = (accept and not checkbox.is_selected()) or (not accept and checkbox.is_selected())
        if should_toggle:
            checkbox.send_keys(Keys.SPACE)

    def agree_to_privacy_policy(self) -> None:
        """Ensures the user has agreed to the privacy policy."""
        self.set_privacy_policy(True)
        checkbox = self.wait.until(EC.presence_of_element_located(self.PRIVACY_POLICY_CHECKBOX))
        assert checkbox.is_selected(), "Privacy policy checkbox should be selected"

    def submit(self) -> None:
        """Clicks Continue."""
        self._click_when_clickable(self.CONTINUE_BUTTON)

    def submit_registration(self) -> None:
        """Old name used by earlier tests."""
        self.submit()

    def fill_registration_form(self, first, last, email, password) -> None:
        """Fills the form fields and accepts the privacy policy (no submit)."""
        self.enter_first_name(first)
        self.enter_last_name(last)
        self.enter_email(email)
        self.enter_password(password)
        self.set_privacy_policy(True)

    def register(
        self,
        first: str,
        last: str,
        email: str,
        password: str,
        accept_privacy_policy: bool = True,
    ) -> None:
        """Fills the form and submits it."""
        self.enter_first_name(first)
        self.enter_last_name(last)
        self.enter_email(email)
        self.enter_password(password)
        self.set_privacy_policy(accept_privacy_policy)
        self.submit()

    # ---------------------------
    # Reads / waits
    # ---------------------------

    def wait_for_success_url(self) -> bool:
        """Waits for success redirect. Returns False if it never happens."""
        try:
            self.wait.until(EC.url_contains("route=account/success"))
            return True
        except Exception:
            return False

    def wait_for_global_warning(self) -> str:
        """Waits for the top warning alert and returns its text."""
        return self.wait.until(EC.visibility_of_element_located(self.GLOBAL_WARNING)).text

    def get_global_warning(self) -> str | None:
        """Returns the top warning alert text if it exists."""
        return self.get_text(self.GLOBAL_WARNING) if self.is_visible(self.GLOBAL_WARNING) else None

    def get_warning_message(self):
        """"Retrieves the current warning message shown to the user."""
        return self.get_global_warning()

    def field_errors(self) -> dict:
        """Returns field errors for firstname, lastname, email, and password."""
        def _safe_text(locator) -> str:
            els = self.driver.find_elements(*locator)
            return els[0].text.strip() if els and els[0].text else ""

        return {
            "firstname": _safe_text(self.ERROR_FIRSTNAME),
            "lastname": _safe_text(self.ERROR_LASTNAME),
            "email": _safe_text(self.ERROR_EMAIL),
            "password": _safe_text(self.ERROR_PASSWORD),
        }

    def wait_for_field_errors(self) -> dict:
        """Waits until at least one field error is visible, then returns all field errors."""
        self.wait.until(EC.visibility_of_any_elements_located(self.FIELD_ERRORS))
        return self.field_errors()

    def wait_for_email_error(self) -> str:
        """Waits for the email error and returns its text."""
        return self.wait.until(EC.visibility_of_element_located(self.ERROR_EMAIL)).text

    def get_field_warnings(self):
        """Retrieves validation error messages displayed next to form fields."""
        return self.get_elements_text(self.FIELD_ERRORS)

    def is_error_displayed_near_name_fields(self) -> bool:
        """True if either First Name or Last Name shows a validation error."""
        errors = self.field_errors()
        return bool(errors.get("firstname") or errors.get("lastname"))
