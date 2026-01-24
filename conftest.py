import logging
import os
import pytest
from selenium import webdriver
from pytest_html import extras as pytest_html_extras


@pytest.fixture(scope="function")
def driver():
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--start-maximized")
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "autofill.profile_enabled": False,
        "autofill.credit_card_enabled": False
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()



@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if call.when == "call":
        if not hasattr(report, "extra"):
            report.extra = []

        if report.failed and "driver" in item.funcargs:
            driver = item.funcargs["driver"]
            screenshot_dir = os.path.join("reports", "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)

            filename = report.nodeid.replace("::", "_").replace("/", "_") + ".png"
            abs_path = os.path.join(screenshot_dir, filename)
            driver.save_screenshot(abs_path)

            relative_path = f"screenshots/{filename}".replace("\\", "/")
            report.extra.append(pytest_html_extras.image(relative_path, mime_type="image/png"))


def pytest_html_results_table_header(cells):
    cells.insert(2, '<th>Screenshot</th>')


def pytest_html_results_table_row(report, cells):
    screenshot_html = ""
    if hasattr(report, "extra"):
        for extra in report.extra:
            if isinstance(extra, dict) and extra.get("format") == "image":
                screenshot_html = extra["content"]
                break
    cells.insert(2, screenshot_html)



def pytest_configure(config):
    reports_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    if not getattr(logger, "_handler_set", False):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger._handler_set = True

