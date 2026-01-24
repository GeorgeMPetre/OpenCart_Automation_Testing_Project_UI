import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.login_page import LoginPage
from pages.main_navigation_menu_page import NavigationPage
from pages.product_page import ProductPage
from utils.db_utils import reset_login_attempts
from utils.soft_assert import SoftAssert


@pytest.mark.checkout
@pytest.mark.ui
class TestCheckoutFlow:
    """Covers the main checkout flow in OpenCart, including happy paths and key edge cases."""

    @pytest.mark.positive
    @pytest.mark.functional
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_01_happy_path_checkout_single_product(self, driver, request):
        """Places an order with one product and confirms the success page is shown."""
        soft_assert = SoftAssert(driver, request)
        wait = WebDriverWait(driver, 10)

        login_page = LoginPage(driver)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        login_page.open()
        login_page.login("validEmail@gmail.com", "ValidPass123")

        navigation_page.open_home()
        navigation_page.open_laptops_and_notebooks()

        product_page.select_product("HP LP3065")
        product_page.add_to_cart()

        navigation_page.open_cart()
        cart_page.proceed_to_checkout()

        checkout_page.complete_new_address_checkout_flow()

        wait.until(EC.url_contains("route=checkout/success"))
        soft_assert.assert_true(
            checkout_page.is_order_successful(),
            "Verify order placed success message.",
        )
        soft_assert.assert_all()

    @pytest.mark.positive
    @pytest.mark.functional
    @pytest.mark.regression
    def test_02_checkout_with_multiple_products(self, driver, request):
        """Places an order with multiple products and confirms checkout still succeeds."""
        soft_assert = SoftAssert(driver, request)
        wait = WebDriverWait(driver, 10)

        login_page = LoginPage(driver)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        login_page.open()
        login_page.login("validEmail@gmail.com", "ValidPass123")

        navigation_page.open_home()
        navigation_page.open_desktops_mac()
        product_page.select_product("iMac")
        product_page.add_to_cart()

        navigation_page.open_laptops_and_notebooks()
        product_page.select_product("MacBook Air")
        product_page.add_to_cart()

        navigation_page.open_cart()
        cart_page.proceed_to_checkout()

        checkout_page.complete_new_address_checkout_flow()

        wait.until(EC.url_contains("route=checkout/success"))
        soft_assert.assert_true(
            checkout_page.is_order_successful(),
            "Verify order success message with multiple products.",
        )
        soft_assert.assert_all()

    @pytest.mark.negative
    @pytest.mark.functional
    @pytest.mark.regression
    def test_03_checkout_with_empty_cart(self, driver, request):
        """Removes the only cart item and confirms checkout cannot proceed from an empty cart."""
        reset_login_attempts("validEmail@gmail.com")

        soft_assert = SoftAssert(driver, request)

        login_page = LoginPage(driver)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        login_page.open()
        login_page.login("validEmail@gmail.com", "ValidPass123")

        navigation_page.open_home()
        navigation_page.open_laptops_and_notebooks()

        product_page.select_product("MacBook Air")
        product_page.add_to_cart()

        navigation_page.open_cart()
        cart_page.remove_product("MacBook Air")

        current_url = driver.current_url
        soft_assert.assert_in(
            "route=checkout/cart",
            current_url,
            f"Verify user stays on cart page when cart is empty. URL: {current_url}",
        )
        soft_assert.assert_all()

    @pytest.mark.positive
    @pytest.mark.functional
    @pytest.mark.regression
    def test_04_edit_cart_quantity_then_checkout(self, driver, request):
        """Updates quantity in cart, then completes checkout and expects success."""
        soft_assert = SoftAssert(driver, request)
        wait = WebDriverWait(driver, 10)

        login_page = LoginPage(driver)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        login_page.open()
        login_page.login("validEmail@gmail.com", "ValidPass123")

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
            "Expected quantity to be 2 in cart.",
        )

        cart_page.proceed_to_checkout()
        checkout_page.complete_new_address_checkout_flow()

        wait.until(EC.url_contains("route=checkout/success"))
        soft_assert.assert_true(
            checkout_page.is_order_successful(),
            "Expected successful checkout after updating quantity.",
        )
        soft_assert.assert_all()

    @pytest.mark.functional
    @pytest.mark.regression
    def test_05_cancel_checkout_and_verify_cart(self, driver, request):
        """Starts checkout, goes back, and confirms the cart still has the product."""
        reset_login_attempts("validEmail@gmail.com")

        soft_assert = SoftAssert(driver, request)
        wait = WebDriverWait(driver, 10)

        login_page = LoginPage(driver)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)

        login_page.open()
        login_page.login("validEmail@gmail.com", "ValidPass123")

        navigation_page.open_home()
        navigation_page.open_laptops_and_notebooks()

        product_page.select_product("HP LP3065")
        product_page.add_to_cart()

        navigation_page.open_cart()
        cart_page.proceed_to_checkout()

        driver.back()

        navigation_page.open_cart()
        wait.until(lambda d: cart_page.is_product_in_cart("HP LP3065"))

        soft_assert.assert_true(
            cart_page.is_product_in_cart("HP LP3065"),
            "Product still present in cart after cancelling checkout.",
        )
        soft_assert.assert_all()

    @pytest.mark.positive
    @pytest.mark.functional
    @pytest.mark.regression
    def test_06_checkout_then_view_order_history(self, driver, request):
        """Completes checkout, then opens order history and checks an entry is shown."""
        reset_login_attempts("validEmail@gmail.com")

        soft_assert = SoftAssert(driver, request)
        wait = WebDriverWait(driver, 10)

        login_page = LoginPage(driver)
        navigation_page = NavigationPage(driver)
        product_page = ProductPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        login_page.open()
        login_page.login("validEmail@gmail.com", "ValidPass123")

        navigation_page.open_home()
        navigation_page.open_laptops_and_notebooks()

        product_page.select_product("MacBook Air")
        product_page.add_to_cart()

        navigation_page.open_cart()
        cart_page.proceed_to_checkout()

        checkout_page.complete_new_address_checkout_flow()

        wait.until(EC.url_contains("route=checkout/success"))
        soft_assert.assert_true(checkout_page.is_order_successful(), "Order should be successful.")

        driver.get("http://localhost/opencart/upload/index.php?route=account/account&language=en-gb")
        navigation_page.open_order_history()

        history_table = wait.until(
            EC.visibility_of_element_located(("css selector", "#content .table-responsive"))
        )
        soft_assert.assert_true(
            "#" in (history_table.text or ""),
            "Expected order history to contain an order entry.",
        )
        soft_assert.assert_all()
