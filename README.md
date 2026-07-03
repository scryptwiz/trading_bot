# Trading Bot — Binance Futures Testnet (USDT-M)

A small, structured Python CLI for placing MARKET, LIMIT, and STOP_LIMIT
orders on Binance Futures Testnet, built for the Primetrade.ai application task.

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py          # Binance client wrapper (API layer)
    orders.py          # Order placement / validation orchestration
    validators.py       # Input validation, independent & unit-testable
    logging_config.py   # Rotating file + console logging setup
  cli.py                # CLI entry point (argparse)
  logs/
    trading_bot.log     # Generated at runtime
  requirements.txt
  .env.example
  README.md
```

The CLI layer (`cli.py`) never talks to Binance directly — it goes through
`OrderManager` which goes through `FuturesTestnetClient`.
This keeps each piece independently testable and makes it easy
to swap the SDK for raw REST calls later without touching the CLI.

## Setup

### 1. Clone and install dependencies
```bash
git clone 'https://github.com/scryptwiz/trading_bot'
cd trading_bot
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure credentials
```bash
cp .env.example .env
# then edit .env and paste in your testnet API key/secret
```
The bot reads `BINANCE_API_KEY` and `BINANCE_API_SECRET` from the environment
(loaded automatically from `.env` via `python-dotenv`).

## Usage

```bash
python cli.py --symbol <SYMBOL> --side <BUY|SELL> --type <MARKET|LIMIT|STOP_LIMIT> --quantity <QTY> [--price <PRICE>] [--stop-price <STOP_PRICE>]
```

### Market order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Limit order
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
```

### Stop-limit order (bonus third order type)
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --price 64000 --stop-price 64500
```

Each run prints:
1. **Order Request Summary** — the normalized parameters about to be sent
2. **Order Response** — `orderId`, `status`, `executedQty`, `avgPrice`, etc.
3. A clear success or failure message

All requests, responses, and errors are also written to `logs/trading_bot.log`
(rotates at 5MB, keeps 3 backups) with timestamps, for audit purposes.

## Error Handling

- **Invalid input** (bad symbol format, missing price on a LIMIT order,
  non-positive quantity, etc.) is caught by `bot/validators.py` before any
  network call is made, and reported as `Invalid input: ...`.
- **API errors** (e.g. insufficient balance, invalid symbol per Binance,
  rate limits) are caught from `BinanceAPIException` / `BinanceOrderException`
  and reported as `Order failed: ...`.
- **Network failures** (timeouts, DNS issues) are caught and reported the
  same way, and logged with a full traceback in `trading_bot.log` for
  debugging (`logger.exception`).
- The CLI never crashes with a raw Python traceback on-screen; unexpected
  exceptions are caught by a last-resort handler in `cli.py`.

## Assumptions

- **STOP_LIMIT was chosen as the bonus order type.** On Binance Futures this
  maps to `type=STOP` with both a `price` (limit price after trigger) and
  `stopPrice` (trigger price).
- Quantity and price precision/step-size (`LOT_SIZE` / `PRICE_FILTER`
  exchange filters) are validated by Binance itself at request time; the
  bot does not pre-fetch `exchangeInfo` to enforce tick size client-side.
  If Binance rejects an order for precision reasons, the API error message
  is surfaced as-is.
- Orders default to `GTC` (Good-Til-Cancelled) time-in-force for LIMIT and
  STOP_LIMIT orders.
- All orders are placed on **USDT-M Futures** (not Coin-M, not Spot).
- Only one-way position mode is assumed (no `positionSide` param is sent);
  if your testnet account is in hedge mode, set it to one-way mode in
  Futures settings, or extend `orders.py` to pass `positionSide`.

## Notes on Log Files

`logs/trading_bot.log` is generated fresh on each run. To produce the
deliverable log files, run one MARKET and one LIMIT order against your own
testnet credentials as shown above — the resulting entries in
`logs/trading_bot.log` (plus the console output) are what should be
submitted alongside the code.
