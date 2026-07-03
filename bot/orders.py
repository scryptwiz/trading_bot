from __future__ import annotations

import logging

from bot.client import BinanceClientError, FuturesTestnetClient
from bot.validators import ValidationError, validate_order_params

logger = logging.getLogger("trading_bot")


class OrderManager:
    def __init__(self, client: FuturesTestnetClient):
        self.client = client

    def build_binance_params(self, validated: dict) -> dict:
        # Translate our normalized param dict into Binance API kwargs.
        params = {
            "symbol": validated["symbol"],
            "side": validated["side"],
            "type": (
                validated["order_type"]
                if validated["order_type"] != "STOP_LIMIT"
                else "STOP"
            ),
            "quantity": str(validated["quantity"]),
        }

        if validated["order_type"] == "LIMIT":
            params["timeInForce"] = "GTC"
            params["price"] = str(validated["price"])

        elif validated["order_type"] == "STOP_LIMIT":
            params["timeInForce"] = "GTC"
            params["price"] = str(validated["price"])
            params["stopPrice"] = str(validated["stop_price"])

        return params

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity,
        price=None,
        stop_price=None,
    ) -> dict:
        validated = validate_order_params(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )

        summary = {
            "symbol": validated["symbol"],
            "side": validated["side"],
            "type": validated["order_type"],
            "quantity": str(validated["quantity"]),
            "price": (
                str(validated["price"])
                if validated["price"] is not None
                else "N/A (market)"
            ),
            "stop_price": (
                str(validated["stop_price"])
                if validated["stop_price"] is not None
                else "N/A"
            ),
        }
        logger.info("Order request summary: %s", summary)

        binance_params = self.build_binance_params(validated)
        response = self.client.place_order(**binance_params)

        result = {
            "orderId": response.get("orderId"),
            "status": response.get("status"),
            "executedQty": response.get("executedQty"),
            "avgPrice": response.get("avgPrice"),
            "symbol": response.get("symbol"),
            "side": response.get("side"),
            "type": response.get("type"),
        }
        return {"summary": summary, "result": result}
