from decimal import Decimal, ROUND_HALF_UP
import pytest
from selenium.webdriver.support.wait import WebDriverWait
from utils.db_utils import reset_login_attempts
from utils.soft_assert import SoftAssert
from pages.login_page import LoginPage
from pages.main_navigation_menu_page import NavigationPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage


def money_eq(actual: float | None, expected: str) -> bool:
    """Compares money values to 2 decimals, so price checks stay stable."""
    if actual is None:
        return False
    a = Decimal(str(actual)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    e = Decimal(expected).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return a == e


@pytest.fixture
def upload_file(tmp_path):
    """Creates a temporary file for upload-required products."""
    p = tmp_path / "upload.txt"
    p.write_text("file upload test", encoding="utf-8")
    return str(p)


@pytest.mark.cart
@pytest.mark.ui
class TestAddEditCartFunctionality:
    """Validates add-to-cart, cart updates, and cart persistence in OpenCart."""

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.smoke
    @pytest.mark.ui
    @pytest.mark.regression
    def test_01_add_single_product_to_cart(self, driver, request):
        """Adds one product and checks name, quantity, and total price in the cart."""
        soft_assert = SoftAssert(driver, request)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        navigation_page.open_home()
        navigation_page.open_laptops_and_notebooks()

        product_page.select_product("HP LP3065")
        product_page.add_to_cart(quantity=1)

        navigation_page.open_cart()

        soft_assert.assert_true(
            cart_page.is_product_in_cart("HP LP3065"),
            "HP LP3065 should appear in the cart",
        )
        soft_assert.assert_equal(
            cart_page.get_product_quantity("HP LP3065"),
            1,
            "Quantity for HP LP3065 should be 1",
        )

        total = cart_page.get_total_price("HP LP3065")
        soft_assert.assert_true(
            money_eq(total, "122.00"),
            f"Total price for HP LP3065 should be 122.00",
        )
        soft_assert.assert_all()

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.ui
    @pytest.mark.regression
    def test_02_add_multiple_quantities(self, driver, request):
        """Adds the same product several times and checks the final quantity."""
        soft_assert = SoftAssert(driver, request)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        navigation_page.open_home()
        navigation_page.open_laptops_and_notebooks()

        product_page.select_product("MacBook")
        for _ in range(3):
            product_page.add_to_cart(quantity=1)

        navigation_page.open_cart()
        cart_page.wait_for_product_quantity("MacBook", 3)

        soft_assert.assert_equal(
            cart_page.get_product_quantity("MacBook"),
            3,
            "Quantity of MacBook should be 3 after adding it three times",
        )
        soft_assert.assert_all()

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.ui
    @pytest.mark.regression
    def test_03_edit_quantity_in_cart(self, driver, request):
        """Edits quantity in the cart and checks the new value is applied."""
        soft_assert = SoftAssert(driver, request)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        navigation_page.open_home()
        navigation_page.open_laptops_and_notebooks()

        product_page.select_product("MacBook")
        product_page.add_to_cart()

        navigation_page.open_cart()

        cart_page.update_quantity("MacBook", 2)
        cart_page.wait_for_product_quantity("MacBook", 2)

        soft_assert.assert_equal(
            cart_page.get_product_quantity("MacBook"),
            2,
            "Product quantity should be updated to 2",
        )
        soft_assert.assert_all()

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.ui
    @pytest.mark.regression
    def test_04_remove_product_from_cart(self, driver, request):
        """Adds a product, removes it, and checks the cart becomes empty."""
        soft_assert = SoftAssert(driver, request)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        navigation_page.open_home()
        navigation_page.open_cameras()

        product_page.select_product("Canon EOS 5D")
        product_page.select_required_dropdown_options()
        product_page.add_to_cart()

        navigation_page.open_cart()
        cart_page.remove_product("Canon EOS 5D")

        soft_assert.assert_false(
            cart_page.is_product_in_cart("Canon EOS 5D"),
            "Product should be removed from cart",
        )
        soft_assert.assert_true(
            cart_page.is_cart_empty_message_displayed(),
            "Empty cart message should be shown after removing product",
        )
        soft_assert.assert_all()

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.ui
    @pytest.mark.regression
    def test_05_cart_persists_after_login(self, driver, request):
        """Adds an item as a guest, logs in, and checks the item is still in the cart."""
        reset_login_attempts("validEmail@gmail.com")

        soft_assert = SoftAssert(driver, request)
        navigation_page = NavigationPage(driver)
        login_page = LoginPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        cart_url = CartPage.CART_URL

        navigation_page.open_home()
        product_page.select_product("iPhone")
        product_page.add_to_cart()

        navigation_page.open_cart()

        soft_assert.assert_true(
            "route=checkout/cart" in driver.current_url,
            f"Expected to be on cart page before login, but URL was: {driver.current_url}",
        )
        soft_assert.assert_true(
            cart_page.is_product_in_cart("iPhone"),
            "Expected iPhone to be in cart BEFORE login (baseline check).",
        )

        login_page.open()
        login_page.login("validEmail@gmail.com", "ValidPass123")

        navigation_page.open_cart()
        if "route=checkout/cart" not in driver.current_url:
            driver.get(cart_url)

        soft_assert.assert_true(
            "route=checkout/cart" in driver.current_url,
            f"Expected to be on cart page after login, but URL was: {driver.current_url}",
        )
        soft_assert.assert_true(
            cart_page.is_product_in_cart("iPhone"),
            "Expected iPhone to still be in cart AFTER login.",
        )
        soft_assert.assert_all()

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.ui
    @pytest.mark.regression
    def test_06_add_multiple_different_products(self, driver, request):
        """Adds two different products and checks both appear in the cart."""
        soft_assert = SoftAssert(driver, request)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        navigation_page.open_home()
        navigation_page.open_desktops_mac()
        product_page.select_product("iMac")
        product_page.add_to_cart()

        navigation_page.open_laptops_and_notebooks()
        product_page.select_product("MacBook Air")
        product_page.add_to_cart()

        navigation_page.open_cart()

        soft_assert.assert_true(cart_page.is_product_in_cart("iMac"), "iMac should be in the cart")
        soft_assert.assert_true(
            cart_page.is_product_in_cart("MacBook Air"),
            "MacBook Air should be in the cart",
        )
        soft_assert.assert_all()

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.boundary
    @pytest.mark.ui
    @pytest.mark.regression
    def test_07_cart_total_price_updates_correctly(self, driver, request):
        """Changes quantity and checks the grand total updates correctly."""
        soft_assert = SoftAssert(driver, request)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        product_name = "MacBook Air"

        navigation_page.open_home()
        navigation_page.open_laptops_and_notebooks()

        product_page.select_product(product_name)
        product_page.add_to_cart()

        navigation_page.open_cart()

        cart_page.update_quantity(product_name, 2)
        cart_page.wait_for_product_quantity(product_name, 2)

        WebDriverWait(driver, 10).until(lambda d: money_eq(cart_page.get_cart_grand_total(), "2404.00"))

        actual_qty = cart_page.get_product_quantity(product_name)
        soft_assert.assert_equal(actual_qty, 2, f"Expected quantity of '{product_name}' to be 2")

        actual_total = cart_page.get_cart_grand_total()
        soft_assert.assert_true(
            money_eq(actual_total, "2404.00"),
            f"Expected cart grand total: 2404.00 but was {actual_total}",
        )
        soft_assert.assert_all()

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.ui
    @pytest.mark.regression
    def test_08_add_product_without_quantity_defaults_to_one(self, driver, request):
        """Adds an item without setting quantity and confirms it defaults to 1."""
        soft_assert = SoftAssert(driver, request)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        navigation_page.open_home()
        product_page.select_product("iPhone")
        product_page.add_to_cart()

        navigation_page.open_cart()

        soft_assert.assert_equal(
            cart_page.get_product_quantity("iPhone"),
            1,
            "Quantity should default to 1 if not specified",
        )
        soft_assert.assert_all()

    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.ui
    @pytest.mark.regression
    def test_09_edit_cart_to_zero_quantity_removes_product(self, driver, request, upload_file):
        """Sets quantity to 0 and checks the cart shows as empty."""
        soft_assert = SoftAssert(driver, request)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        navigation_page.open_home()
        product_page.select_product('Apple Cinema 30"')

        product_page.fill_default_options(upload_file_path=upload_file)
        product_page.add_to_cart()

        navigation_page.open_cart()

        cart_page.update_quantity('Apple Cinema 30"', 0)

        soft_assert.assert_true(
            cart_page.is_cart_empty_message_displayed(),
            "Expected to see 'Your shopping cart is empty!' after setting quantity to 0",
        )
        soft_assert.assert_all()

    @pytest.mark.functional
    @pytest.mark.ui
    @pytest.mark.regression
    def test_10_cart_empty_state_visual_validation(self, driver, request):
        """Opens an empty cart and checks the message and layout are OK."""
        soft_assert = SoftAssert(driver, request)
        navigation_page = NavigationPage(driver)
        cart_page = CartPage(driver)

        navigation_page.open_home()
        navigation_page.open_cart()

        soft_assert.assert_true(
            cart_page.is_cart_empty_message_displayed(),
            "Cart empty message should be visible when no items are in cart",
        )
        soft_assert.assert_true(
            cart_page.is_cart_layout_correct_when_empty(),
            "Layout should not be broken in empty cart state",
        )
        soft_assert.assert_all()
