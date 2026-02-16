import pytest
from utils.soft_assert import SoftAssert


@pytest.mark.ci
@pytest.mark.smoke
def test_ci_soft_assert_no_driver():
    soft = SoftAssert(driver=None, request=None)
    soft.assert_true(True, "Expected True")
    soft.assert_equal("a", "a", "Expected a")
    soft.assert_all()
