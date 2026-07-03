from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}

# Basic check for a USDT-M perpetual symbol
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{2,17}USDT$")


class ValidationError(ValueError):
    """Raised when user-supplied order parameters fail validation."""


def validate_symbol(symbol: str) -> str:
    if not symbol:
        raise ValidationError("Symbol is required (e.g. BTCUSDT).")
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected a USDT-M pair like 'BTCUSDT'."
        )
    return symbol


def validate_side(side: str) -> str:
    if not side:
        raise ValidationError("Side is required (BUY or SELL).")
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of {sorted(VALID_SIDES)}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    if not order_type:
        raise ValidationError("Order type is required (MARKET, LIMIT, or STOP_LIMIT).")
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type


def _to_positive_decimal(value, field_name: str) -> Decimal:
    try:
        dec = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValidationError(f"{field_name} must be a valid number, got '{value}'.")
    if dec <= 0:
        raise ValidationError(f"{field_name} must be greater than 0, got '{value}'.")
    return dec


def validate_quantity(quantity) -> Decimal:
    return _to_positive_decimal(quantity, "Quantity")


def validate_price(price, order_type: str) -> Decimal | None:
    if order_type == "MARKET":
        if price is not None:
            raise ValidationError("Price must not be provided for MARKET orders.")
        return None

    if price is None:
        raise ValidationError(f"Price is required for {order_type} orders.")
    return _to_positive_decimal(price, "Price")


def validate_stop_price(stop_price, order_type: str) -> Decimal | None:
    if order_type != "STOP_LIMIT":
        if stop_price is not None:
            raise ValidationError("Stop price is only valid for STOP_LIMIT orders.")
        return None

    if stop_price is None:
        raise ValidationError("Stop price is required for STOP_LIMIT orders.")
    return _to_positive_decimal(stop_price, "Stop price")


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity,
    price=None,
    stop_price=None,
) -> dict:
    """Run all validators and it return a normalised dict of parameters."""
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_type = validate_order_type(order_type)
    clean_qty = validate_quantity(quantity)
    clean_price = validate_price(price, clean_type)
    clean_stop_price = validate_stop_price(stop_price, clean_type)

    return {
        "symbol": clean_symbol,
        "side": clean_side,
        "order_type": clean_type,
        "quantity": clean_qty,
        "price": clean_price,
        "stop_price": clean_stop_price,
    }
