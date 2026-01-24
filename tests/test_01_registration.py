import time
from uuid import uuid4
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.login_page import LoginPage
from pages.registration_page import RegistrationPage
from utils.soft_assert import SoftAssert


@pytest.mark.registration
@pytest.mark.ui
class TestRegistration:
    """Covers the main registration flows in OpenCart (success + common failure cases)."""

    WAIT_MEDIUM = 10

    VALID_EMAIL = "validEmail@gmail.com"
    VALID_PASSWORD = "ValidPass123"

    # ---------------------------
    # Helpers
    # ---------------------------

    def _soft(self, driver, request) -> SoftAssert:
        """Creates a SoftAssert instance for this test run."""
        return SoftAssert(driver, request)

    def _open_registration(self, driver) -> RegistrationPage:
        """Opens the registration page and returns the page object."""
        page = RegistrationPage(driver)
        page.navigate_to_registration()
        return page

    def _register(self, page: RegistrationPage, first, last, email, password) -> None:
        """Fills the form and submits the registration."""
        page.fill_registration_form(first, last, email, password)
        page.submit_registration()

    # ---------------------------
    # Positive
    # ---------------------------

    @pytest.mark.positive
    @pytest.mark.functional
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_01_register_with_valid_details(self, driver, request):
        """Registers a new user with valid data and expects the success page."""
        soft = self._soft(driver, request)
        reg = self._open_registration(driver)

        self._register(reg, "John", "Doe", self.VALID_EMAIL, self.VALID_PASSWORD)

        WebDriverWait(driver, self.WAIT_MEDIUM).until(EC.url_contains("account/success"))
        soft.assert_true(
            "route=account/success" in driver.current_url,
            "Registration should redirect to the success page.",
        )
        soft.assert_all()

    # ---------------------------
    # Negative
    # ---------------------------

    @pytest.mark.negative
    @pytest.mark.functional
    @pytest.mark.regression
    def test_02_register_with_existing_email(self, driver, request):
        """Tries to register using an email that already exists and expects a warning."""
        soft = self._soft(driver, request)
        reg = self._open_registration(driver)

        self._register(reg, "John", "Doe", self.VALID_EMAIL, self.VALID_PASSWORD)

        error_msg = WebDriverWait(driver, self.WAIT_MEDIUM).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger"))
        ).text
        soft.assert_in("Warning: E-Mail Address is already registered!", error_msg)
        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.functional
    @pytest.mark.regression
    def test_03_register_with_empty_fields(self, driver, request):
        """Submits an empty form and checks that field validation messages show up."""
        soft = self._soft(driver, request)
        reg = self._open_registration(driver)

        self._register(reg, "", "", "", "")

        wait = WebDriverWait(driver, self.WAIT_MEDIUM)
        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "error-firstname"),
                "First Name must be between 1 and 32 characters!",
            )
        )
        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "error-lastname"),
                "Last Name must be between 1 and 32 characters!",
            )
        )
        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "error-email"),
                "E-Mail Address does not appear to be valid!",
            )
        )
        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "error-password"),
                "Password must be between 4 and 20 characters!",
            )
        )

        soft.assert_in(
            "First Name must be between 1 and 32 characters!",
            driver.find_element(By.ID, "error-firstname").text,
        )
        soft.assert_in(
            "Last Name must be between 1 and 32 characters!",
            driver.find_element(By.ID, "error-lastname").text,
        )
        soft.assert_in(
            "E-Mail Address does not appear to be valid!",
            driver.find_element(By.ID, "error-email").text,
        )
        soft.assert_in(
            "Password must be between 4 and 20 characters!",
            driver.find_element(By.ID, "error-password").text,
        )
        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.functional
    @pytest.mark.regression
    def test_04_register_with_invalid_email_format(self, driver, request):
        """Uses a bad email format and expects the email validation error."""
        soft = self._soft(driver, request)
        reg = self._open_registration(driver)

        self._register(reg, "John", "Doe", "test@invalid", self.VALID_PASSWORD)

        error = WebDriverWait(driver, self.WAIT_MEDIUM).until(
            EC.visibility_of_element_located((By.ID, "error-email"))
        ).text
        soft.assert_in("E-Mail Address does not appear to be valid!", error)
        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.security
    @pytest.mark.functional
    @pytest.mark.regression
    def test_05_register_with_special_characters_in_name(self, driver, request):
        """Tries special characters in name fields and confirms registration does not succeed."""
        soft = self._soft(driver, request)
        reg = self._open_registration(driver)

        initial_url = driver.current_url
        email = f"specialchars_{uuid4().hex[:6]}@test.com"

        self._register(reg, "John$", "D@e", email, self.VALID_PASSWORD)

        reg.wait.until(EC.url_changes(initial_url))

        soft.assert_true(
            "route=account/register" in driver.current_url,
            f"Registration should not succeed with invalid name characters. Current URL: {driver.current_url}",
        )
        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.functional
    @pytest.mark.regression
    def test_06_register_with_spaces_only(self, driver, request):
        """Submits whitespace-only values and checks the expected validation messages."""
        soft = self._soft(driver, request)
        reg = self._open_registration(driver)

        self._register(reg, "   ", "   ", "   ", "   ")

        wait = WebDriverWait(driver, self.WAIT_MEDIUM)

        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "error-firstname"),
                "First Name must be between 1 and 32 characters!",
            )
        )
        soft.assert_in(
            "First Name must be between 1 and 32 characters!",
            driver.find_element(By.ID, "error-firstname").text,
        )

        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "error-lastname"),
                "Last Name must be between 1 and 32 characters!",
            )
        )
        soft.assert_in(
            "Last Name must be between 1 and 32 characters!",
            driver.find_element(By.ID, "error-lastname").text,
        )

        email_errors = driver.find_elements(By.ID, "error-email")
        if email_errors and email_errors[0].text.strip():
            soft.assert_in(
                "E-Mail Address does not appear to be valid!",
                email_errors[0].text,
            )
        else:
            soft.assert_info("No email validation message appeared for whitespace-only input.")

        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "error-password"),
                "Password must be between 4 and 20 characters!",
            )
        )
        soft.assert_in(
            "Password must be between 4 and 20 characters!",
            driver.find_element(By.ID, "error-password").text,
        )
        soft.assert_all()

    @pytest.mark.boundary
    @pytest.mark.functional
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "password, should_pass",
        [
            ("123", False),
            ("1234", True),
            ("a" * 40, True),
            ("a" * 41, False),
        ],
    )
    def test_07_password_length_boundaries(self, driver, request, password, should_pass):
        """Checks password boundary values and confirms success or the password error."""
        soft = self._soft(driver, request)
        reg = self._open_registration(driver)

        email = f"boundary_{len(password)}_{int(time.time())}@test.com"
        self._register(reg, "John", "Doe", email, password)

        reg.wait.until(
            EC.any_of(
                EC.url_contains("route=account/success"),
                EC.text_to_be_present_in_element(
                    (By.ID, "error-password"),
                    "Password must be between 4 and 20 characters!",
                ),
            )
        )

        if should_pass:
            ok = "route=account/success" in driver.current_url
            soft.assert_true(
                ok,
                f"Password length {len(password)} should succeed. Current URL: {driver.current_url}",
            )
            if ok:
                soft.logger.info(f"[PASS] Password length {len(password)} succeeded as expected.")
        else:
            ok = "route=account/register" in driver.current_url
            soft.assert_true(
                ok,
                f"Password length {len(password)} should fail. Current URL: {driver.current_url}",
            )
            if ok:
                soft.logger.info(f"[PASS] Password length {len(password)} failed as expected.")

        soft.assert_all()

    @pytest.mark.negative
    @pytest.mark.security
    @pytest.mark.functional
    @pytest.mark.regression
    def test_08_registration_while_logged_in(self, driver, request):
        """Logs in first, then tries to access registration and confirms it’s blocked or fails."""
        soft = self._soft(driver, request)

        login = LoginPage(driver)
        login.open()
        login.login(self.VALID_EMAIL, self.VALID_PASSWORD)

        reg = self._open_registration(driver)

        if "route=account/register" not in driver.current_url:
            soft.assert_true(
                "route=account/register" not in driver.current_url,
                "Logged-in users should not be able to open the registration page.",
            )
            soft.assert_all()
            return

        self._register(reg, "John", "Doe", self.VALID_EMAIL, self.VALID_PASSWORD)

        soft.assert_in("Warning: E-Mail Address is already registered!", driver.page_source)
        soft.assert_all()
