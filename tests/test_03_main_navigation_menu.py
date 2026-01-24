import pytest
from pages.login_page import LoginPage
from pages.main_navigation_menu_page import NavigationPage
from utils.db_utils import reset_login_attempts
from utils.soft_assert import SoftAssert


@pytest.mark.navigation
@pytest.mark.ui
class TestNavigation:
    """Checks the header navigation, category links, and account pages in OpenCart."""

    USER_EMAIL = "validEmail@gmail.com"
    USER_PASSWORD = "ValidPass123"

    @pytest.fixture()
    def nav(self, driver) -> NavigationPage:
        """Provides the navigation page object."""
        return NavigationPage(driver)

    @pytest.fixture()
    def soft(self, driver, request) -> SoftAssert:
        """Provides soft assertions for each test."""
        return SoftAssert(driver, request)

    @pytest.fixture()
    def login(self, driver) -> LoginPage:
        """Provides the login page object."""
        return LoginPage(driver)

    @pytest.fixture()
    def authenticated(self, login, nav):
        """Logs in and returns a navigation object on a stable authenticated page."""
        reset_login_attempts(self.USER_EMAIL)

        login.open()
        login.login(self.USER_EMAIL, self.USER_PASSWORD)

        nav.open_account_dashboard()
        return nav

    # ---------------------------
    # Header / Unauthenticated
    # ---------------------------

    @pytest.mark.functional
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_01_change_currency_to_euro(self, nav, soft):
        """Switches currency to EUR and checks the UI updates."""
        nav.ensure_home()
        nav.set_currency_euro()

        soft.assert_true(nav.is_currency_euro(), "Prices should show EUR symbol.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_02_my_account_unauthenticated_opens_login(self, nav, soft):
        """Opens My Account while logged out and expects the login page."""
        nav.open_home()
        nav.open_login_from_header()

        soft.assert_true(nav.is_content_visible(), "Login page content should be visible.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_03_wishlist_unauthenticated_redirects_to_login(self, nav, soft):
        """Opens Wish List while logged out and expects a redirect to login."""
        nav.open_home()
        nav.open_wishlist()

        soft.assert_true(nav.is_redirected_to_login(), "Expected redirect to login.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_04_open_cart(self, nav, soft):
        """Opens the shopping cart from the header and checks the page loads."""
        nav.open_home()
        nav.open_cart()

        soft.assert_true(nav.is_content_visible(), "Cart page content should be visible.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_05_checkout_unauthenticated_empty_cart(self, nav, soft, driver):
        """Opens Checkout while logged out with an empty cart and expects redirect to cart."""
        nav.open_home()
        nav.open_checkout()

        soft.assert_true("checkout/cart" in driver.current_url, "Expected redirect to cart.")
        soft.assert_true(nav.is_empty_cart_message_visible(), "Expected empty cart message.")
        soft.assert_all()

    # ---------------------------
    # Categories
    # ---------------------------

    @pytest.mark.functional
    @pytest.mark.regression
    def test_06_navigate_to_desktops(self, nav, soft):
        """Opens the Desktops category and checks content is visible."""
        nav.open_home()
        nav.open_desktops_mac()

        soft.assert_true(nav.is_content_visible(), "Category page content should be visible.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_07_navigate_to_laptops_and_notebooks(self, nav, soft):
        """Opens Laptops & Notebooks and checks content is visible."""
        nav.open_home()
        nav.open_laptops_and_notebooks()

        soft.assert_true(nav.is_content_visible(), "Category page content should be visible.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_08_navigate_to_components(self, nav, soft):
        """Opens Components and checks content is visible."""
        nav.open_home()
        nav.open_components()

        soft.assert_true(nav.is_content_visible(), "Category page content should be visible.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_09_navigate_to_tablets(self, nav, soft):
        """Opens Tablets and checks content is visible."""
        nav.open_home()
        nav.open_tablets()

        soft.assert_true(nav.is_content_visible(), "Category page content should be visible.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_10_navigate_to_software(self, nav, soft):
        """Opens Software and checks content is visible."""
        nav.open_home()
        nav.open_software()

        soft.assert_true(nav.is_content_visible(), "Category page content should be visible.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_11_navigate_to_phones_and_pdas(self, nav, soft):
        """Opens Phones & PDAs and checks content is visible."""
        nav.open_home()
        nav.open_phones_and_pdas()

        soft.assert_true(nav.is_content_visible(), "Category page content should be visible.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_12_navigate_to_cameras(self, nav, soft):
        """Opens Cameras and checks content is visible."""
        nav.open_home()
        nav.open_cameras()

        soft.assert_true(nav.is_content_visible(), "Category page content should be visible.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_13_navigate_to_mp3_players(self, nav, soft):
        """Opens MP3 Players and checks content is visible."""
        nav.open_home()
        nav.open_mp3_players()

        soft.assert_true(nav.is_content_visible(), "Category page content should be visible.")
        soft.assert_all()

    # ---------------------------
    # Account / Authenticated
    # ---------------------------

    @pytest.mark.functional
    @pytest.mark.regression
    def test_14_account_dashboard_authenticated(self, authenticated, soft):
        """Checks the account dashboard loads after login."""
        soft.assert_true(authenticated.is_content_visible(), "Account dashboard content should be visible.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_15_edit_account_authenticated(self, authenticated, soft):
        """Opens Edit Account and checks the correct page is shown."""
        authenticated.open_edit_account()

        soft.assert_true(authenticated.on_edit_account(), "Expected Edit Account page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_16_change_password_authenticated(self, authenticated, soft):
        """Opens Change Password and checks the correct page is shown."""
        authenticated.open_change_password()

        soft.assert_true(authenticated.on_change_password(), "Expected Change Password page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_17_payment_methods_authenticated(self, authenticated, soft):
        """Opens Payment Methods and checks the page loads."""
        authenticated.open_payment_methods()

        soft.assert_true(authenticated.on_payment_methods(), "Expected Payment Methods page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_18_address_book_authenticated(self, authenticated, soft):
        """Opens Address Book and checks the page loads."""
        authenticated.open_address_book()

        soft.assert_true(authenticated.on_address_book(), "Expected Address Book page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_19_wishlist_authenticated(self, authenticated, soft):
        """Opens Wish List while logged in and checks the page loads."""
        authenticated.open_account_wishlist()

        soft.assert_true(authenticated.on_account_wishlist(), "Expected Wishlist page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_20_order_history_authenticated(self, authenticated, soft):
        """Opens Order History and checks the page loads."""
        authenticated.open_order_history()

        soft.assert_true(authenticated.on_order_history(), "Expected Order History page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_21_subscriptions_authenticated(self, authenticated, soft):
        """Opens Subscriptions and checks the page loads."""
        authenticated.open_subscriptions()

        soft.assert_true(authenticated.subscriptions_visible(), "Expected Subscriptions page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_22_downloads_authenticated(self, authenticated, soft):
        """Opens Downloads and checks the page loads."""
        authenticated.open_downloads()

        soft.assert_true(authenticated.downloads_visible(), "Expected Downloads page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_23_reward_points_authenticated(self, authenticated, soft):
        """Opens Reward Points and checks the page loads."""
        authenticated.open_reward_points()

        soft.assert_true(authenticated.on_reward_points(), "Expected Reward Points page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_24_return_requests_authenticated(self, authenticated, soft):
        """Opens Returns and checks the page loads."""
        authenticated.open_return_requests()

        soft.assert_true(authenticated.on_return_requests(), "Expected Returns page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_25_transactions_authenticated(self, authenticated, soft):
        """Opens Transactions and checks the page loads."""
        authenticated.open_transactions()

        soft.assert_true(authenticated.on_transactions(), "Expected Transactions page.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_26_affiliate_account_page_authenticated(self, authenticated, soft):
        """Opens the Affiliate page and checks the page loads."""
        authenticated.open_affiliate()

        soft.assert_true(authenticated.on_affiliate_page(), "Expected Affiliate page to be displayed.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_27_affiliate_register_authenticated(self, authenticated, soft):
        """Registers an affiliate account and checks the success message."""
        authenticated.open_affiliate()
        authenticated.register_affiliate(
            company="Test Company Ltd",
            website="http://example.com",
            tax_id="TX123456",
            payment_method="Cheque",
            cheque_payee_name="Jean Doe",
        )

        soft.assert_true(authenticated.affiliate_success(), "Expected affiliate update success.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_28_newsletter_subscription_authenticated(self, authenticated, soft):
        """Updates newsletter subscription and checks the success message."""
        authenticated.open_newsletter()
        authenticated.set_newsletter(subscribe=True)

        soft.assert_true(authenticated.newsletter_success(), "Expected newsletter update success.")
        soft.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_29_logout(self, authenticated, soft):
        """Logs out and confirms the user is signed out."""
        authenticated.logout()

        soft.assert_true(authenticated.is_logged_out(), "Expected user to be logged out.")
        soft.assert_all()
