"""Minimal page objects for saucedemo.com (locators use the site's data-test attributes)."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = "https://www.saucedemo.com/"
PASSWORD = "secret_sauce"
TIMEOUT = 15


def dt(name):
    return (By.CSS_SELECTOR, f'[data-test="{name}"]')


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUT)

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def logout(self):
        self.click((By.ID, "react-burger-menu-btn"))
        self.click(dt("logout-sidebar-link"))


class LoginPage(BasePage):
    def open(self):
        self.driver.get(BASE_URL)
        return self

    def login(self, user, password=PASSWORD):
        self.type(dt("username"), user)
        self.type(dt("password"), password)
        self.click(dt("login-button"))

    def error_text(self):
        return self.find(dt("error")).text


class InventoryPage(BasePage):
    SORT = dt("product-sort-container")
    BADGE = dt("shopping-cart-badge")

    def title(self):
        return self.find(dt("title")).text

    def names(self):
        els = self.wait.until(EC.presence_of_all_elements_located(dt("inventory-item-name")))
        return [e.text for e in els]

    def prices(self):
        els = self.driver.find_elements(*dt("inventory-item-price"))
        return [float(e.text.replace("$", "")) for e in els]

    def sort_by(self, value):  # az | za | lohi | hilo
        Select(self.find(self.SORT)).select_by_value(value)

    def add(self, slug):
        self.click(dt(f"add-to-cart-{slug}"))

    def remove(self, slug):
        self.click(dt(f"remove-{slug}"))

    def badge_count(self):
        els = self.driver.find_elements(*self.BADGE)
        return int(els[0].text) if els else 0

    def open_cart(self):
        self.click(dt("shopping-cart-link"))


class CartPage(BasePage):
    def item_names(self):
        self.find(dt("title"))
        return [e.text for e in self.driver.find_elements(*dt("inventory-item-name"))]

    def remove(self, slug):
        self.click(dt(f"remove-{slug}"))

    def checkout(self):
        self.click(dt("checkout"))


class CheckoutPage(BasePage):
    def fill_info(self, first, last, postal):
        self.type(dt("firstName"), first)
        self.type(dt("lastName"), last)
        self.type(dt("postalCode"), postal)

    def continue_(self):
        self.click(dt("continue"))

    def error_text(self):
        return self.find(dt("error")).text

    def amount(self, label):  # subtotal-label | tax-label | total-label
        return float(self.find(dt(label)).text.split("$")[1])

    def finish(self):
        self.click(dt("finish"))

    def complete_header(self):
        return self.find(dt("complete-header")).text
