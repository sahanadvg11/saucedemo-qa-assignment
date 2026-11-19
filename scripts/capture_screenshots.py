"""Reproduces each seeded bug on saucedemo.com, saves a screenshot per bug into docs/screenshots/,
and writes what it actually observed into the 'Actual Result' section of each bug report.

Usage: python scripts/capture_screenshots.py          (add --headed to watch the browser)
"""
import re
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "docs" / "screenshots"
BUGS = ROOT / "docs" / "bug-reports"
URL = "https://www.saucedemo.com/"
PW = "secret_sauce"


def dt(n):
    return (By.CSS_SELECTOR, f'[data-test="{n}"]')


def make_driver(headed):
    o = Options()
    if not headed:
        o.add_argument("--headless=new")
    o.add_argument("--window-size=1400,1000")
    o.add_experimental_option("prefs", {"credentials_enable_service": False,
                                        "profile.password_manager_enabled": False,
                                        "profile.password_manager_leak_detection": False})
    return webdriver.Chrome(options=o)


def wait(d, loc, t=20):
    return WebDriverWait(d, t).until(EC.visibility_of_element_located(loc))


def login(d, user):
    d.get(URL)
    wait(d, dt("username")).send_keys(user)
    d.find_element(*dt("password")).send_keys(PW)
    t0 = time.time()
    d.find_element(*dt("login-button")).click()
    wait(d, dt("inventory-container"), 40)
    return round(time.time() - t0, 2)


def names(d):
    return [e.text for e in d.find_elements(*dt("inventory-item-name"))]


def shot(d, bug):
    SHOTS.mkdir(parents=True, exist_ok=True)
    d.save_screenshot(str(SHOTS / f"{bug}.png"))
    print(f"  screenshot saved: docs/screenshots/{bug}.png")


def set_actual(bug, text):
    p = BUGS / f"{bug}.md"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"(## Actual Result\n).*?(\n\n## Screenshot)", lambda m: m.group(1) + text + m.group(2),
               s, flags=re.S)
    s = re.sub(r"\n> Draft:.*\n?", "\n", s)
    p.write_text(s, encoding="utf-8")


def bug001(d):
    login(d, "problem_user")
    srcs = [i.get_attribute("src").split("/")[-1] for i in d.find_elements(By.CSS_SELECTOR, ".inventory_item img")]
    shot(d, "BUG-001")
    same = len(set(srcs)) == 1
    set_actual("BUG-001", (f"All {len(srcs)} products show the same image file ({srcs[0]})." if same else
                           f"Image files observed: {sorted(set(srcs))}. (Bug NOT reproduced as drafted - review.)"))
    return same


def bug002(d):
    login(d, "problem_user")
    before = names(d)
    Select(wait(d, dt("product-sort-container"))).select_by_value("za")
    time.sleep(1)
    after = names(d)
    shot(d, "BUG-002")
    ok = after == sorted(before, reverse=True)
    set_actual("BUG-002", f"Before sorting: {before}. After selecting 'Name (Z to A)': {after}. "
                          + ("Sorted correctly (bug NOT reproduced - review)." if ok else "The order is not Z to A."))
    return not ok


def bug003(d):
    login(d, "problem_user")
    slugs = [e.get_attribute("data-test").replace("add-to-cart-", "")
             for e in d.find_elements(By.CSS_SELECTOR, '[data-test^="add-to-cart-"]')]
    add_fail, remove_fail = [], []
    for s in slugs:
        d.find_element(*dt(f"add-to-cart-{s}")).click()
        time.sleep(0.4)
        if not d.find_elements(*dt(f"remove-{s}")):
            add_fail.append(s)
    badge = d.find_elements(*dt("shopping-cart-badge"))
    badge_txt = badge[0].text if badge else "none"
    shot(d, "BUG-003")
    for s in slugs:
        if d.find_elements(*dt(f"remove-{s}")):
            d.find_element(*dt(f"remove-{s}")).click()
            time.sleep(0.4)
            if d.find_elements(*dt(f"remove-{s}")):
                remove_fail.append(s)
    set_actual("BUG-003", f"Clicked Add to cart on all {len(slugs)} products; cart badge shows {badge_txt}. "
                          f"Products whose button did not change to Remove: {add_fail or 'none'}. "
                          f"Products where Remove did not work: {remove_fail or 'none'}.")
    return bool(add_fail or remove_fail)


def bug004(d):
    login(d, "problem_user")
    d.find_element(*dt("add-to-cart-sauce-labs-backpack")).click()
    d.find_element(*dt("shopping-cart-link")).click()
    d.find_element(*dt("checkout")).click()
    wait(d, dt("firstName")).send_keys("Test")
    d.find_element(*dt("lastName")).send_keys("User")
    d.find_element(*dt("postalCode")).send_keys("560001")
    first = d.find_element(*dt("firstName")).get_attribute("value")
    last = d.find_element(*dt("lastName")).get_attribute("value")
    d.find_element(*dt("continue")).click()
    time.sleep(1)
    err = d.find_elements(*dt("error"))
    shot(d, "BUG-004")
    blocked = "checkout-step-two" not in d.current_url
    set_actual("BUG-004", f"After typing First='Test', Last='User', Postal='560001', the fields contain "
                          f"First='{first}', Last='{last}'. After Continue, URL is {d.current_url}"
                          + (f" with error: {err[0].text}" if err else "") + ".")
    return blocked


def bug005(d):
    std = login(d, "standard_user")
    d.delete_all_cookies()
    slow = login(d, "performance_glitch_user")
    shot(d, "BUG-005")
    set_actual("BUG-005", f"Login with performance_glitch_user took about {slow} s versus {std} s for "
                          f"standard_user, with no loading indicator on the Login button.")
    return slow > std + 1


def bug006(d):
    login(d, "standard_user")
    d.find_element(*dt("shopping-cart-link")).click()
    d.find_element(*dt("checkout")).click()
    reached = "checkout-step-one" in d.current_url
    wait(d, dt("firstName")).send_keys("Test")
    d.find_element(*dt("lastName")).send_keys("User")
    d.find_element(*dt("postalCode")).send_keys("560001")
    d.find_element(*dt("continue")).click()
    wait(d, dt("finish")).click()
    done = wait(d, dt("complete-header")).text
    shot(d, "BUG-006")
    set_actual("BUG-006", f"With an empty cart, Checkout opened {'step one' if reached else 'no checkout page'} "
                          f"and the order was completed with the message: '{done}'.")
    return reached


def main():
    headed = "--headed" in sys.argv
    results = {}
    for name, fn in [("BUG-001", bug001), ("BUG-002", bug002), ("BUG-003", bug003),
                     ("BUG-004", bug004), ("BUG-005", bug005), ("BUG-006", bug006)]:
        print(f"{name} ...")
        d = make_driver(headed)
        try:
            results[name] = fn(d)
        except Exception as e:  # keep going; report at the end
            results[name] = f"ERROR: {e}"
            print("  failed:", e)
        finally:
            d.quit()
    print("\nSummary (True = bug reproduced):")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("\nOpen docs/screenshots and docs/bug-reports to review before publishing.")


if __name__ == "__main__":
    main()
