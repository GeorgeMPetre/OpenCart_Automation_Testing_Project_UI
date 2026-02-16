import logging
import os
import pytest
from selenium import webdriver
from pytest_html import extras as pytest_html_extras
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "firefox", "edge"],
    )
    parser.addoption(
        "--drivers-dir",
        action="store",
        default=None,
        help="Folder containing chromedriver.exe / geckodriver.exe / msedgedriver.exe",
    )


def _default_drivers_dir():
    project_root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(project_root, "drivers")


@pytest.fixture(scope="function")
def driver(request):
    browser = request.config.getoption("--browser")
    drivers_dir = request.config.getoption("--drivers-dir") or _default_drivers_dir()

    drv = None

    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        driver_path = os.path.join(drivers_dir, "chromedriver.exe")
        if os.path.exists(driver_path):
            drv = webdriver.Chrome(service=ChromeService(driver_path), options=options)
        else:
            drv = webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        driver_path = os.path.join(drivers_dir, "geckodriver.exe")
        if os.path.exists(driver_path):
            drv = webdriver.Firefox(service=FirefoxService(driver_path), options=options)
        else:
            drv = webdriver.Firefox(options=options)
        drv.maximize_window()

    elif browser == "edge":
        options = EdgeOptions()
        driver_path = os.path.join(drivers_dir, "msedgedriver.exe")
        if os.path.exists(driver_path):
            drv = webdriver.Edge(service=EdgeService(driver_path), options=options)
        else:
            drv = webdriver.Edge(options=options)
        drv.maximize_window()

    drv.implicitly_wait(10)
    yield drv
    drv.quit()



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

