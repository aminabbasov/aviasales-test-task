from decimal import Decimal

import pytest

from src.core.normalizers import ExponentialMovingAverage


@pytest.fixture
def EMA():
    return ExponentialMovingAverage(alpha=Decimal("0.5"))


def test_assert_alpha():
    with pytest.raises(AssertionError):
        ExponentialMovingAverage(alpha=Decimal("1.01"))


def test_none_mean_update(EMA):
    EMA.update(new_value=Decimal("100"))
    assert EMA.mean == Decimal("100")


def test_none_mean_normalize(EMA):
    assert EMA.normalize(value=Decimal("100")) == Decimal("100")


def test_mean_update(EMA):
    EMA.update(new_value=Decimal("100"))
    EMA.update(new_value=Decimal("50"))
    assert EMA.mean == Decimal("75")


def test_mean_normalize(EMA):
    EMA.update(new_value=Decimal("100"))
    assert EMA.normalize(value=Decimal("50")) == Decimal("-0.5")
