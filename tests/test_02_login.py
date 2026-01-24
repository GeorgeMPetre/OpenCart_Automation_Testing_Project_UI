import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.login_page import LoginPage
from utils.db_utils import reset_login_attempts
from utils.soft_assert import SoftAssert


@pytest.mark.login
@pytest.mark.ui
class TestLogin:
    """Covers the main login flows in OpenCart (success, failures, and basic security checks)."""

    VALID_EMAIL = "validEmail@gmail.com"
    VALID_PASSWORD = "ValidPass123"
    WAIT_MEDIUM = 10

    # ---------------------------
    # Helpers
    # ---------------------------

    def _soft(self, driver, request) -> SoftAssert:
        """Creates a SoftAssert instance for this test run."""
        return SoftAssert(driver, request)

    def _open_login(self, driver) -> LoginPage:
        """Opens the login page and returns the page object."""
        return LoginPage(driver).open()

    def _reset_attempts(self) -> None:
        """Clears login attempt tracking for the test user."""
        reset_login_attempts(self.VALID_EMAIL)

    # ---------------------------
    # Positive
    # ---------------------------

    @pytest.mark.positive
    @pytest.mark.functional
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_01_login_with_valid_credentials(self, driver, request):
        """Logs in with valid credentials and expects the account dashboard."""
        self._reset_attempts()

        soft = self._soft(driver, request)
        page = self._open_login(driver).login(self.VALID_EMAIL, self.VALID_PASSWORD)

        soft.assert_true(
            page.wait_for_dashboard(),
            "Expected user to be redirected to account dashboard after login.",
        )
        soft.assert_all()

    @pytest.mark.positive
    @pytest.mark.functional
    @pytest.mark.regression
    def test_02_login_with_uppercase_email(self, driver, request):
        """Logs in using an uppercase email and expects it to still work."""
        self._reset_attempts()

        soft = self._soft(driver, request)
        page = self._open_login(driver).login(self.VALID_EMAIL.upper(), self.VALID_PASSWORD)

        soft.assert_true(
            page.wait_for_dashboard(),
            "Expected uppercase email to be accepted and redirect to dashboard.",
        )
        soft.assert_all()

    @pytest.mark.positive
    @pytest.mark.functional
    @pytest.mark.regression
    def test_03_login_with_spaces_in_credentials(self, driver, request):
        """Logs in with extra spaces around input and expects the app to handle it."""
        self._reset_attempts()

        soft = self._soft(driver, request)
        page = self._open_login(driver).login(
            f"  {self.VALID_EMAIL}  ",
            f"  {self.VALID_PASSWORD}  ",
        )

        soft.assert_true(
            page.wait_for_dashboard(),
            "Expected credentials with surrounding spaces to be trimmed and login to succeed.",
        )
        soft.assert_all()

    # ---------------------------
    # Negative
    # ---------------------------

    @pytest.mark.negative
    @pytest.mark.functional
    @pytest.mark.regression
    def test_04_login_with_incorrect_password(self, driver, request):
        """Tries a wrong password and confirms the warning shows and login does not happen."""
        self._reset_attempts()

        soft = self._soft(driver, request)
        page = self._open_login(driver).login(self.VALID_EMAIL, "WrongPass").wait_for_error_alert()
        msg = page.get_error_message()

        soft.assert_in("Warning: No match", msg, "Expected warning message for incorrect password.")
        soft.assert_true(
            page.is_on_login_page(),
            "Expected user to remain on login page after failed login.",
        )
        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.functional
    @pytest.mark.regression
    def test_05_login_with_blank_fields(self, driver, request):
        """Submits empty email/password and checks that login stays blocked with a warning."""
        self._reset_attempts()

        soft = self._soft(driver, request)
        page = self._open_login(driver).login("", "").wait_for_error_alert()
        msg = page.get_error_message().lower()

        soft.assert_true(
            ("warning: no match" in msg) or ("exceeded allowed number of login attempts" in msg),
            "Expected 'No match' warning or rate-limit warning for blank fields.",
        )
        soft.assert_true(
            page.is_on_login_page(),
            "Expected user to remain on login page after failed login.",
        )
        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.functional
    @pytest.mark.regression
    def test_06_login_with_unregistered_email(self, driver, request):
        """Tries a random email and confirms the app rejects it with a warning."""
        soft = self._soft(driver, request)
        page = self._open_login(driver).login("nonexistent@example.com", "AnyPassword").wait_for_error_alert()
        msg = page.get_error_message().lower()

        soft.assert_true(
            ("warning: no match" in msg) or ("exceeded allowed number of login attempts" in msg),
            "Expected warning for unregistered email.",
        )
        soft.assert_true(
            page.is_on_login_page(),
            "Expected user to remain on login page after failed login.",
        )
        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.security
    @pytest.mark.functional
    @pytest.mark.regression
    def test_07_login_sql_injection_with_existing_email(self, driver, request):
        """Uses a simple SQL injection string in password and confirms login still fails."""
        self._reset_attempts()

        soft = self._soft(driver, request)
        page = self._open_login(driver).login(self.VALID_EMAIL, "' OR '1'='1").wait_for_error_alert()
        msg = page.get_error_message().lower()

        soft.assert_in("warning", msg, "Expected warning for SQL injection attempt in password field.")
        soft.assert_true(
            page.is_on_login_page(),
            "Expected user to remain on login page after failed login.",
        )
        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.security
    @pytest.mark.functional
    @pytest.mark.regression
    def test_08_login_sql_injection_in_email_field(self, driver, request):
        """Uses a suspicious email input and confirms the app does not bypass login."""
        soft = self._soft(driver, request)
        page = self._open_login(driver).login("email'or1=1@example.com", "any_password").wait_for_error_alert()
        msg = page.get_error_message().lower()

        soft.assert_in("warning", msg, "Expected warning for SQL injection attempt in email field.")
        soft.assert_true(
            page.is_on_login_page(),
            "Expected user to remain on login page after failed login.",
        )
        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.edge
    @pytest.mark.functional
    @pytest.mark.regression
    def test_09_login_after_multiple_failed_attempts(self, driver, request):
        """Repeats failed logins and checks the app starts blocking or warning more aggressively."""
        self._reset_attempts()

        soft = self._soft(driver, request)
        page = self._open_login(driver)

        for _ in range(5):
            page.login(self.VALID_EMAIL, "WrongPass")

        page.wait_for_error_alert()
        msg = page.get_error_message().lower()

        soft.assert_true(
            page.is_on_login_page() or ("warning" in msg),
            "Expected login to remain blocked or warning displayed after multiple failures.",
        )
        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.security
    @pytest.mark.functional
    @pytest.mark.regression
    def test_10_access_login_while_logged_in(self, driver, request):
        """Logs in, then tries to open the login page again and expects a redirect to account."""
        self._reset_attempts()

        soft = self._soft(driver, request)
        page = self._open_login(driver).login(self.VALID_EMAIL, self.VALID_PASSWORD)

        soft.assert_true(
            page.wait_for_dashboard(),
            "Precondition failed: user should be logged in before redirect validation.",
        )

        LoginPage(driver).open_while_logged_in()

        WebDriverWait(driver, self.WAIT_MEDIUM).until(EC.url_contains("route=account/account"))
        soft.assert_true(
            "route=account/account" in driver.current_url,
            "Expected redirect to account dashboard when visiting login page while logged in.",
        )
        soft.assert_all()
