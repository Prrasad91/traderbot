# TraderBot — Detailed Manual

> **Repository:** `Prrasad91/traderbot` — `src` folder
>
> This README is a comprehensive user manual for TraderBot. It covers architecture, setup, configuration, usage, deployment, testing, troubleshooting, and contribution guidelines. Treat this as the authoritative guide for installing, running, and extending the bot.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Architecture & Code Layout](#architecture--code-layout)
4. [Prerequisites](#prerequisites)
5. [Installation (Developer Setup)](#installation-developer-setup)
6. [Configuration](#configuration)
7. [Running the Bot](#running-the-bot)
8. [Core Components & How They Work](#core-components--how-they-work)
9. [Trading Strategies & Examples](#trading-strategies--examples)
10. [Risk Management & Safety](#risk-management--safety)
11. [Logging, Monitoring & Alerts](#logging-monitoring--alerts)
12. [Testing](#testing)
13. [Deployment Recommendations](#deployment-recommendations)
14. [Common Issues & Troubleshooting](#common-issues--troubleshooting)
15. [Extending the Bot / Adding Strategies](#extending-the-bot--adding-strategies)
16. [Security Considerations](#security-considerations)
17. [Contributing](#contributing)
18. [License](#license)
19. [FAQ](#faq)

---

## Project Overview

TraderBot is a modular algorithmic trading framework intended to be used (and extended) by individual traders and developers. It contains a collection of modules for data ingestion, signal generation (strategies), order execution, risk management, logging and backtesting stubs. The `src` folder contains the code for the live system and local development.

> **Goal:** Provide a small, well-structured foundation that can connect to data sources and broker APIs (e.g., Zerodha, Alpaca), generate trade signals, and route orders with configurable risk controls.


## Key Features

- Modular strategy interface — swap strategies without changing core engine
- Data ingestion adapters (CSV / historical / live feed adapter stub)
- Execution adapter (broker abstraction layer)
- Position sizing and risk management utilities
- Logging and structured error handling
- Config-driven operation via environment variables and config files
- Unit-testable components and example test cases


## Architecture & Code Layout

High-level layout (based on the `src` folder):

```
src/
├─ engine/              # Core trading engine (orchestrator)
├─ strategies/          # Strategy implementations (strategy interface + examples)
├─ data/                # Data adapters (historical, live feed wrappers)
├─ brokers/             # Broker adapters (Zerodha, paper broker, mock)
├─ utils/               # Utilities: indicators, math, logging
├─ config/              # Configuration helpers and defaults
├─ tests/               # Unit / integration tests
└─ main.py              # Command-line entrypoint (example)
```

Each package should have an `__init__.py` and clear public functions/classes.


## Prerequisites

Install the following on your development machine:

- Python 3.10+ (3.11 recommended)
- `pip` or `poetry` / `pipenv` (choose one dependency manager)
- Git
- Optional: Docker (for containerized deployment)

Python packages commonly used (example):

- pandas
- numpy
- requests / aiohttp (for REST/websocket)
- python-dotenv
- pytest
- loguru or builtin `logging`


## Installation (Developer Setup)

1. Clone the repository:

```bash
git clone https://github.com/Prrasad91/traderbot.git
cd traderbot/src
```

2. Create virtual environment and install dependencies (example with venv):

```bash
python -m venv .venv
source .venv/bin/activate    # Linux / macOS
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

If `requirements.txt` is not present, create one with the packages you need.

3. Copy environment example and set secrets:

```bash
cp .env.example .env
# edit .env with API keys, account ids, mode (paper/live)
```


## Configuration

TraderBot reads configuration from environment variables and optionally a YAML/JSON config file. Important configuration keys (suggested names):

- `TRADER_MODE` — `paper` or `live`
- `BROKER` — `zerodha` | `mock` | `alpaca` etc.
- `ZERODHA_API_KEY` / `ZERODHA_SECRET` / `ZERODHA_ACCESS_TOKEN`
- `DATA_SOURCE` — `historical_csv` | `realtime_ws` | `mock`
- `DEFAULT_RISK_PER_TRADE` — decimal or percent (e.g., `0.01` for 1%)
- `LOG_LEVEL` — `INFO`, `DEBUG` etc.

Place secrets only in `.env` (not in git). Use `.gitignore` to ignore `.env` and other secrets.


## Running the Bot

The repo includes a `main.py` entrypoint to run the engine. The typical modes are:

- `dev` / single-run backtest using historical CSV
- `paper` — run live with a mock broker for validation
- `live` — connect to an actual broker's live APIs (use with great care)

Example commands:

```bash
# Run in paper mode
TRADER_MODE=paper python main.py --config config/local.yaml

# Run a single backtest on local data
python main.py --backtest --data data/historical/NIFTY_1min.csv --strategy strategies/sample_strategy.py
```

The `main.py` should accept CLI flags for configuration path, strategy selection, and run mode.


## Core Components & How They Work

### Engine
The engine is the orchestrator. Responsibilities:
- load configuration and environment
- initialize data adapters and broker adapters
- schedule or stream market data
- feed data to strategies
- receive signals from strategies and forward to risk manager
- place orders via broker adapter
- maintain positions & P&L

Important engine interfaces to implement/expect:

```python
class Engine:
    def __init__(self, data_adapter, broker_adapter, strategy, risk_manager, logger):
        ...
    def run(self):
        # main loop or event-driven run
        ...
    def stop(self):
        ...
```


### Strategies
Each strategy must implement a standard interface (Simplified example):

```python
class StrategyBase:
    def __init__(self, config):
        pass
    def on_new_bar(self, bar):
        # return signals like {'symbol':'NIFTY', 'side':'BUY', 'size': 1}
        pass
    def on_order_update(self, order_info):
        pass
```

Provide at least one example strategy in `strategies/` such as `moving_average_crossover.py` or `rsi_mean_reversion.py`.


### Data Adapters
Data adapters abstract the source of market data. Provide adapters for:
- Historical CSV files (for backtesting)
- Websocket REST feeds (for live streaming)
- Mock generator (randomized or replayed market data)

Each adapter should implement a generator-like API producing bars or ticks.


### Broker Adapters
The broker adapter maps generic order requests from engine to broker-specific REST or websocket calls. Key functions:

- `connect()` / `authenticate()`
- `place_order(order)`
- `cancel_order(order_id)`
- `get_positions()`
- `get_order_status(order_id)`

Implement a safe `MockBroker` for development and paper trading.


### Risk Manager
Central place to enforce risk and sizing rules. Example responsibilities:

- compute position size from `DEFAULT_RISK_PER_TRADE`
- enforce max position limits and exposure per symbol
- enforce stop-loss / trailing stop rules
- reject or modify orders that violate risk rules


## Trading Strategies & Examples

Include documented example strategies with parameterized configuration so users can run and tweak them.

Example: Simple Moving Average Crossover strategy

- Parameters: `short_window`, `long_window`, `symbol`
- Signal: buy when short MA crosses above long MA; sell on crossover down

Pseudo-code sample:

```python
class MovingAverageCrossover(StrategyBase):
    def __init__(self, short_window=9, long_window=21):
        ...
    def on_new_bar(self, bar):
        update_mas(bar.close)
        if crossup:
            return Signal('BUY')
        if crossdown:
            return Signal('SELL')
```


## Risk Management & Safety

- **Paper test thoroughly** before enabling `live` mode.
- Use `DEFAULT_RISK_PER_TRADE` to cap loss exposure.
- Implement "circuit-breaker" logic to stop trading for the day after X consecutive losses or after a drawdown threshold.
- Always use stop-loss orders where possible, and verify the broker supports guaranteed stops if required.


## Logging, Monitoring & Alerts

- Use structured logging (`json` or `loguru`) so logs can be parsed.
- Log at least: signals generated, orders sent, order updates, rejections, account state, and exceptions.
- Consider external monitoring (Prometheus + Grafana) or simple email/Telegram alerts for critical failures and large P&L swings.

Example of log event structure:

```json
{
  "timestamp": "2025-10-04T12:00:00+05:30",
  "event": "order_placed",
  "symbol": "NIFTY",
  "side": "BUY",
  "qty": 1,
  "price": 21000,
  "order_id": "abc-123"
}
```


## Testing

- Unit tests for utils, indicators, and strategy functions using `pytest`.
- Integration tests with `MockBroker` and `MockDataFeed` to simulate end-to-end flows.

Run tests:

```bash
pytest -q
```


## Deployment Recommendations

- Use containerization (Docker) for production deployments. Create a small Dockerfile that installs the same runtime and runs your CLI with env variables.
- Prefer hosted VMs with reliable network connectivity for live trading.
- Use process managers (systemd, supervisor, or Docker restart policy) to keep the bot running.
- Backup logs and rotate them daily.

Example Dockerfile snippet:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY src/ /app/
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```


## Common Issues & Troubleshooting

- **Authentication failures to broker:** ensure API key/secret and time-synced clocks; check broker tokens have not expired.
- **Order rejected:** check order parameters, margin, symbol codes and available margin.
- **Large slippage in live trades:** use limit orders or set smaller market order sizes; check liquidity for instrument.
- **Data feed gap / missing bars:** implement resume/replay from last known timestamp and alert on gaps.


## Extending the Bot / Adding Strategies

1. Create a new file under `strategies/` implementing the `StrategyBase` interface.
2. Add configuration for the strategy in `config/strategies.yaml`.
3. Add unit tests under `tests/` that exercise the strategy logic using deterministic mock data.
4. Run through paper mode and/or local backtest before pushing to `main` branch.

Checklist for a new strategy:

- ✅ deterministic behavior for same input
- ✅ documented parameters
- ✅ tests for edge cases
- ✅ integration with risk manager


## Security Considerations

- Never commit API keys or `.env` into version control.
- Use environment secrets in your CI/CD for deployment.
- Limit permissions on API keys (e.g., disable withdrawals if possible).
- Rotate credentials periodically.


## Contributing

- Fork the repo and create feature branches.
- Write clear unit tests and documentation for new features.
- Follow code style (PEP8) and keep commits small and descriptive.
- Open pull requests with a description of changes and testing performed.


## License

Specify your desired license in `LICENSE` (e.g., MIT). If the repository currently has no license, add one and indicate usage permissions.


## FAQ

**Q: Is this safe to use with real money?**
A: Use extreme caution. Paper test thoroughly and run a long period of simulated testing with realistic slippage and fills before moving to live.

**Q: Which brokers are supported?**
A: Out-of-the-box: none. Implement a `brokers/zerodha_adapter.py` and a `MockBroker` first. The README above contains the methods your adapter must implement.

**Q: Can I backtest with the code here?**
A: Yes — build/extend the CSV data adapter, run `main.py --backtest` and plug in an output P&L recorder.


---

### Quick checklist before going live

- [ ] Add `.env` with correct keys and `TRADER_MODE=paper`
- [ ] Implement or configure a `MockBroker` and `MockDataFeed`
- [ ] Run unit/integration tests (`pytest`)
- [ ] Run a paper simulation for at least 30 trading days of data
- [ ] Add logging and crash recovery
- [ ] Deploy behind a process manager or container


---

If you want, I can:
- generate `examples/` with ready-to-run scripts
- scaffold `requirements.txt`, `.env.example`, `Dockerfile`, and `CI` (GitHub Actions) workflows
- create a short `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`

Tell me which of the above you'd like me to add next and I will create them in this repo's `src` structure.

