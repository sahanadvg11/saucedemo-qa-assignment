"""UI automation for https://www.saucedemo.com (Selenium + pytest).

Each test's docstring lists the manual test case (docs/test-cases.md) it automates.
"""
import pytest
from selenium.webdriver.support.ui import WebDriverWait

from .pages import (BASE_URL, CartPage, CheckoutPage, InventoryPage, LoginPage)

pytestmark = pytest.mark.ui

BACKPACK = "sauce-labs-backpack"
BIKE_LIGHT = "sauce-labs-bike-light"
ONESIE = "sauce-labs-onesie"


@pytest.fixture
def login(driver):
    def _login(user="standard_user"):
        LoginPage(driver).open().login(user)
        return InventoryPage(driver)
    return _login


# ---------------------------------------------------------------- Login
def test_tc01_valid_login(driver, login):
    """TC01 - valid login lands on the inventory page."""
    inv = login()
    assert "/inventory.html" in driver.current_url
    assert inv.title() == "Products"
    assert len(inv.names()) == 6


def test_tc02_locked_out_user(driver):
    """TC02 - locked_out_user sees lock-out error and stays on login."""
    page = LoginPage(driver).open()
    page.login("locked_out_user")
    assert "locked out" in page.error_text()
    assert "/inventory.html" not in driver.current_url


@pytest.mark.parametrize(
    "user,password,expected",
    [
        ("standard_user", "wrong_password", "do not match any user"),  # TC03
        ("no_such_user", "secret_sauce", "do not match any user"),     # TC04
        ("", "secret_sauce", "Username is required"),                  # TC05
        ("standard_user", "", "Password is required"),                 # TC06
        ("", "", "Username is required"),                              # TC07
        ("Standard_User", "secret_sauce", "do not match any user"),    # TC08 case-sensitive
        ("' OR 1=1 --", "x", "do not match any user"),                 # TC09 injection string
    ],
    ids=["tc03-bad-pw", "tc04-unknown-user", "tc05-empty-user", "tc06-empty-pw",
         "tc07-both-empty", "tc08-case-sensitive", "tc09-sql-chars"],
)
def test_login_negative(driver, user, password, expected):
    """TC03-TC09 - negative login scenarios show the correct error and block access."""
    page = LoginPage(driver).open()
    page.login(user, password)
    assert expected in page.error_text()
    assert "/inventory.html" not in driver.current_url


def test_tc11_direct_url_requires_login(driver):
    """TC11 - opening /inventory.html while logged out redirects to login with an error."""
    driver.get(BASE_URL + "inventory.html")
    page = LoginPage(driver)
    assert "only access '/inventory.html' when you are logged in" in page.error_text()


def test_tc12_logout(driver, login):
    """TC12 - logout returns to the login page."""
    inv = login()
    inv.logout()
    WebDriverWait(driver, 10).until(lambda d: d.current_url.rstrip("/") == BASE_URL.rstrip("/"))


# ---------------------------------------------------------------- Listing / sorting
def test_tc16_sort_name_az(driver, login):
    """TC16 - Name (A to Z) sorts alphabetically."""
    inv = login()
    inv.sort_by("az")
    assert inv.names() == sorted(inv.names())


def test_tc17_sort_name_za(driver, login):
    """TC17 - Name (Z to A) sorts reverse alphabetically."""
    inv = login()
    inv.sort_by("za")
    assert inv.names() == sorted(inv.names(), reverse=True)


def test_tc18_sort_price_low_high(driver, login):
    """TC18 - Price (low to high) sorts ascending."""
    inv = login()
    inv.sort_by("lohi")
    assert inv.prices() == sorted(inv.prices())


def test_tc19_sort_price_high_low(driver, login):
    """TC19 - Price (high to low) sorts descending."""
    inv = login()
    inv.sort_by("hilo")
    assert inv.prices() == sorted(inv.prices(), reverse=True)


# ---------------------------------------------------------------- Cart
def test_tc23_24_add_items_updates_badge_and_cart(driver, login):
    """TC23/TC24 - adding items updates the badge and cart contents."""
    inv = login()
    inv.add(BACKPACK)
    assert inv.badge_count() == 1
    inv.add(BIKE_LIGHT)
    assert inv.badge_count() == 2
    inv.open_cart()
    assert sorted(CartPage(driver).item_names()) == ["Sauce Labs Backpack", "Sauce Labs Bike Light"]


def test_tc25_remove_from_listing(driver, login):
    """TC25 - removing from the listing clears the badge."""
    inv = login()
    inv.add(BACKPACK)
    inv.remove(BACKPACK)
    assert inv.badge_count() == 0


def test_tc26_remove_from_cart_page(driver, login):
    """TC26 - removing on the cart page updates the list."""
    inv = login()
    inv.add(BACKPACK)
    inv.add(ONESIE)
    inv.open_cart()
    cart = CartPage(driver)
    cart.remove(BACKPACK)
    assert cart.item_names() == ["Sauce Labs Onesie"]


def test_tc27_cart_persists_after_refresh(driver, login):
    """TC27 - cart contents survive a page refresh."""
    inv = login()
    inv.add(BACKPACK)
    driver.refresh()
    assert InventoryPage(driver).badge_count() == 1


# ---------------------------------------------------------------- Checkout
def _to_checkout(driver, login, *slugs):
    inv = login()
    for s in slugs:
        inv.add(s)
    inv.open_cart()
    CartPage(driver).checkout()
    return CheckoutPage(driver)


def test_tc30_happy_path_purchase(driver, login):
    """TC30 - complete purchase shows the confirmation message."""
    co = _to_checkout(driver, login, BACKPACK)
    co.fill_info("Test", "User", "560001")
    co.continue_()
    co.finish()
    assert co.complete_header() == "Thank you for your order!"


@pytest.mark.parametrize(
    "first,last,postal,expected",
    [
        ("", "User", "560001", "First Name is required"),   # TC31
        ("Test", "", "560001", "Last Name is required"),    # TC32
        ("Test", "User", "", "Postal Code is required"),    # TC33
    ],
    ids=["tc31-no-first", "tc32-no-last", "tc33-no-postal"],
)
def test_checkout_required_fields(driver, login, first, last, postal, expected):
    """TC31-TC33 - each required checkout field is validated."""
    co = _to_checkout(driver, login, BACKPACK)
    co.fill_info(first, last, postal)
    co.continue_()
    assert expected in co.error_text()


def test_tc35_order_total_math(driver, login):
    """TC35 - item total is the sum of prices and total = item total + tax."""
    co = _to_checkout(driver, login, BACKPACK, BIKE_LIGHT)  # 29.99 + 9.99
    co.fill_info("Test", "User", "560001")
    co.continue_()
    subtotal, tax, total = (co.amount(x) for x in ("subtotal-label", "tax-label", "total-label"))
    assert subtotal == pytest.approx(39.98)
    assert tax == pytest.approx(round(subtotal * 0.08, 2), abs=0.01)
    assert total == pytest.approx(subtotal + tax, abs=0.01)


@pytest.mark.xfail(reason="Known behaviour: site allows checkout with an empty cart (see docs/bug-reports/BUG-006)",
                   strict=False)
def test_tc37_empty_cart_checkout_is_blocked(driver, login):
    """TC37 - checkout with an empty cart should be blocked (expected to FAIL on this site)."""
    inv = login()
    inv.open_cart()
    CartPage(driver).checkout()
    assert "checkout-step-one" not in driver.current_url


# ---------------------------------------------------------------- Seeded-bug users (documented as xfail)
@pytest.mark.xfail(reason="BUG-002: problem_user sort does not reorder products", strict=False)
def test_tc22_problem_user_sort_works(driver, login):
    """TC22 - problem_user sorting by name Z-A should reorder products."""
    inv = login("problem_user")
    inv.sort_by("za")
    assert inv.names() == sorted(inv.names(), reverse=True)


@pytest.mark.xfail(reason="BUG-004: problem_user cannot enter Last Name at checkout", strict=False)
def test_tc41_problem_user_checkout_last_name(driver, login):
    """TC41 - problem_user should be able to complete checkout step one."""
    inv = login("problem_user")
    inv.add(BACKPACK)
    inv.open_cart()
    CartPage(driver).checkout()
    co = CheckoutPage(driver)
    co.fill_info("Test", "User", "560001")
    co.continue_()
    assert "checkout-step-two" in driver.current_url
