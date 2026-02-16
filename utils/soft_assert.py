import os
import uuid
from datetime import datetime
from pytest_html import extras
from utils.logger import get_logger
import sys

class SoftAssert:
    def __init__(self, driver, request):
        self._infos = []
        self._errors = []
        self.driver = driver
        self.request = request
        self.logger = get_logger()
        self.screenshot_dir = os.path.join("reports", "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _capture_screenshot(self, label):
        try:
            current_node = self.request.node
        except Exception:
            return None
        if not hasattr(current_node, "extra"):
            current_node.extra = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{label}_{timestamp}_{uuid.uuid4().hex[:6]}.png"
        abs_path = os.path.join(self.screenshot_dir, filename)
        self.driver.save_screenshot(abs_path)
        relative_path = f"screenshots/{filename}".replace("\\", "/")
        current_node.extra.append(extras.image(relative_path, mime_type='image/png'))
        return relative_path

    def assert_true(self, condition, message=""):
        message = message or "Expected condition to be True"
        try:
            assert condition, message
        except AssertionError as e:
            error_msg = f"[ASSERT_TRUE FAIL] {str(e)}"
            self.logger.error(error_msg, stacklevel=2)
            self._errors.append((error_msg, None))
        else:
            self.logger.info(f"[PASS] {message}", stacklevel=2)
        sys.stdout.flush()
        sys.stderr.flush()

    def assert_false(self, condition, message=""):
        message = message or "Expected condition to be False"
        try:
            assert not condition, message
            self.logger.info(f"[PASS] {message}", stacklevel=2)
        except AssertionError as e:
            path = self._capture_screenshot("assert_false_fail")
            error_msg = f"[ASSERT_FALSE FAIL] {str(e)}"
            self.logger.error(error_msg, stacklevel=2)
            self._errors.append((error_msg, path))

    def assert_equal(self, actual, expected, message=""):
        message = message or f"Expected '{actual}' to equal '{expected}'"
        try:
            assert actual == expected, message
            self.logger.info(f"[PASS] {message}", stacklevel=2)
        except AssertionError as e:
            path = self._capture_screenshot("assert_equal_fail")
            error_msg = f"[ASSERT_EQUAL FAIL] {str(e)}"
            self.logger.error(error_msg, stacklevel=2)
            self._errors.append((error_msg, path))

    def assert_in(self, member, container, message=""):
        message = message or f"Expected '{member}' to be in '{container}'"
        try:
            assert member in container, message
            self.logger.info(f"[PASS] {message}", stacklevel=2)
        except AssertionError as e:
            path = self._capture_screenshot("assert_in_fail")
            error_msg = f"[ASSERT_IN FAIL] {str(e)}"
            self.logger.error(error_msg, stacklevel=2)
            self._errors.append((error_msg, path))

    def assert_info(self, *args):
        if len(args) == 1:
            condition = True
            message = args[0]
        elif len(args) == 2:
            condition, message = args
        else:
            raise TypeError("assert_info() takes 1 or 2 arguments")

        if condition:
            info_msg = f"[PASS] {message}"
            self.logger.info(info_msg, stacklevel=2)
            self._infos.append((info_msg, None))

    def assert_all(self):
        for msg, path in self._infos:
            print(f"{msg}\nScreenshot: {path}")
        if self._errors:
            error_details = "\n\n".join(msg for msg, _ in self._errors)
            raise AssertionError("Soft assertion errors occurred:\n" + error_details)

    def assert_not_in(self, unexpected, actual, message=""):
        try:
            assert unexpected not in actual, message or f"Did not expect '{unexpected}' in '{actual}'"
        except AssertionError as e:
            self._errors.append(f"[ASSERT_NOT_IN FAIL] {message or str(e)}")
