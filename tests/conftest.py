"""Shared fixtures. Driver is created per UI test; screenshot saved on failure."""
import os
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def driver(request):
    opts = Options()
    if os.getenv("HEADED") != "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # Disable Chrome's password-manager popups which can block clicks
    opts.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        },
    )
    drv = webdriver.Chrome(options=opts)  # Selenium Manager fetches the driver
    yield drv
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        ARTIFACTS.mkdir(exist_ok=True)
        drv.save_screenshot(str(ARTIFACTS / f"{request.node.name}.png"))
    drv.quit()
