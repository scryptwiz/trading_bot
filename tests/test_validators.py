import sys
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.validators import ValidationError, validate_order_params  # noqa: E402


def test_valid_market_order():
    result = validate_order_params("btcusdt", "buy", "market", "0.01")
    assert result["symbol"] == "BTCUSDT"
    assert result["side"] == "BUY"
    assert result["order_type"] == "MARKET"
    assert result["quantity"] == Decimal("0.01")
    assert result["price"] is None


def test_valid_limit_order():
    result = validate_order_params("BTCUSDT", "SELL", "LIMIT", "0.01", "65000")
    assert result["price"] == Decimal("65000")


def test_valid_stop_limit_order():
    result = validate_order_params("ETHUSDT", "BUY", "STOP_LIMIT", "1", "3000", "3050")
    assert result["price"] == Decimal("3000")
    assert result["stop_price"] == Decimal("3050")


def test_limit_order_missing_price_raises():
    with pytest.raises(ValidationError):
        validate_order_params("BTCUSDT", "SELL", "LIMIT", "0.01")


def test_market_order_with_price_raises():
    with pytest.raises(ValidationError):
        validate_order_params("BTCUSDT", "BUY", "MARKET", "0.01", "65000")


def test_invalid_symbol_raises():
    with pytest.raises(ValidationError):
        validate_order_params("BTC", "BUY", "MARKET", "0.01")


def test_invalid_side_raises():
    with pytest.raises(ValidationError):
        validate_order_params("BTCUSDT", "HOLD", "MARKET", "0.01")


def test_invalid_order_type_raises():
    with pytest.raises(ValidationError):
        validate_order_params("BTCUSDT", "BUY", "TWAP", "0.01")


def test_non_positive_quantity_raises():
    with pytest.raises(ValidationError):
        validate_order_params("BTCUSDT", "BUY", "MARKET", "0")
    with pytest.raises(ValidationError):
        validate_order_params("BTCUSDT", "BUY", "MARKET", "-5")


def test_non_numeric_quantity_raises():
    with pytest.raises(ValidationError):
        validate_order_params("BTCUSDT", "BUY", "MARKET", "abc")


def test_stop_limit_missing_stop_price_raises():
    with pytest.raises(ValidationError):
        validate_order_params("BTCUSDT", "BUY", "STOP_LIMIT", "0.01", "65000")
