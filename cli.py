from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from bot.client import BinanceClientError, FuturesTestnetClient
from bot.logging_config import setup_logger
from bot.orders import OrderManager
from bot.validators import ValidationError

load_dotenv()

logger = setup_logger()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place MARKET / LIMIT / STOP_LIMIT orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"])
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
    )
    parser.add_argument("--quantity", required=True, help="Order quantity, e.g. 0.01")
    parser.add_argument(
        "--price", required=False, help="Limit price (required for LIMIT / STOP_LIMIT)"
    )
    parser.add_argument(
        "--stop-price",
        dest="stop_price",
        required=False,
        help="Trigger price (required for STOP_LIMIT)",
    )
    return parser


def print_summary(summary: dict) -> None:
    print("\n--- Order Request Summary ---")
    for key, value in summary.items():
        print(f"{key:>12}: {value}")


def print_result(result: dict) -> None:
    print("\n--- Order Response ---")
    for key, value in result.items():
        print(f"{key:>12}: {value}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        client = FuturesTestnetClient()
        manager = OrderManager(client)

        outcome = manager.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )

        print_summary(outcome["summary"])
        print_result(outcome["result"])
        print("\nOrder placed successfully.\n")
        return 0

    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
        print(f"\nInvalid input: {exc}\n")
        return 1

    except BinanceClientError as exc:
        logger.error("Order failed: %s", exc)
        print(f"\nOrder failed: {exc}\n")
        return 1

    except KeyboardInterrupt:
        print("\nCancelled by user.")
        return 130

    except Exception as exc:
        logger.exception("Unexpected error")
        print(f"\nUnexpected error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
