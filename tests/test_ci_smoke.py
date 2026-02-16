from urllib import request

import pytest
from utils.soft_assert import SoftAssert

@pytest.mark.ci
@pytest.mark.smoke
def test_soft_assert_basic(driver):
    soft = SoftAssert(driver, request)
    soft.assert_true(True, "Expected True")
    soft.assert_equal("a", "a", "Expected a")
