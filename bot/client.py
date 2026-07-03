from __future__ import annotations

import logging
import os

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

logger = logging.getLogger("trading_bot")

FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised for any failure talking to the Binance Futures Testnet API."""


class FuturesTestnetClient:
    def __init__(self, api_key: str | None = None, api_secret: str | None = None):
        api_key = api_key or os.getenv("BINANCE_API_KEY")
        api_secret = api_secret or os.getenv("BINANCE_API_SECRET")

        if not api_key or not api_secret:
            raise BinanceClientError(
                "Missing API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET "
                "as environment variables (or in a .env file)."
            )

        try:
            self._client = Client(api_key, api_secret, testnet=True, ping=False)
            self._client.FUTURES_URL = FUTURES_TESTNET_BASE_URL + "/fapi"
        except Exception as exc:
            logger.error("Failed to initialize Binance client: %s", exc)
            raise BinanceClientError(
                f"Failed to initialize Binance client: {exc}"
            ) from exc

        logger.debug(
            "Initialized FuturesTestnetClient against %s", FUTURES_TESTNET_BASE_URL
        )

    def place_order(self, **params) -> dict:
        logger.info("Submitting order request: %s", params)
        try:
            response = self._client.futures_create_order(**params)
            logger.info("Order response: %s", response)
            return response
        except BinanceAPIException as exc:
            logger.error("Binance API error placing order: %s", exc)
            raise BinanceClientError(
                f"Binance API error: {exc.message} (code {exc.code})"
            ) from exc
        except BinanceOrderException as exc:
            logger.error("Binance order error: %s", exc)
            raise BinanceClientError(f"Binance order error: {exc}") from exc
        except Exception as exc:  # network errors, timeouts, etc.
            logger.error("Unexpected/network error placing order: %s", exc)
            raise BinanceClientError(f"Network or unexpected error: {exc}") from exc

    def get_order_status(self, symbol: str, order_id: int) -> dict:
        logger.info("Fetching order status for symbol=%s order_id=%s", symbol, order_id)
        try:
            response = self._client.futures_get_order(symbol=symbol, orderId=order_id)
            logger.info("Order status response: %s", response)
            return response
        except BinanceAPIException as exc:
            logger.error("Binance API error fetching order status: %s", exc)
            raise BinanceClientError(
                f"Binance API error: {exc.message} (code {exc.code})"
            ) from exc
        except Exception as exc:
            logger.error("Unexpected/network error fetching order status: %s", exc)
            raise BinanceClientError(f"Network or unexpected error: {exc}") from exc
