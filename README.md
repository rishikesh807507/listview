# Listview — Indian Stocks & IPO Intelligence

> **Comprehensive Indian Stock Market & IPO Intelligence Platform**  
> Real-time stock analytics, interactive TradingView charts, IPO & unofficial Grey Market Premium (GMP) tracking, machine-learning-driven directional forecasting, fundamental screener, portfolio simulation, and quantitative algorithmic backtesting.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

---

## 📑 Table of Contents

- [Overview & Core Value](#-overview--core-value)
- [Key Features](#-key-features)
- [Architecture & Data Flow](#-architecture--data-flow)
- [Technology Stack](#-technology-stack)
- [Zero Paid APIs & Data Attribution](#-zero-paid-apis--data-attribution)
- [Prerequisites & Requirements](#-prerequisites--requirements)
- [Local Installation & Setup](#-local-installation--setup)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Database Initialization](#2-database-initialization)
  - [3. Frontend Setup](#3-frontend-setup)
- [Configuration (.env.example)](#-configuration-envexample)
- [Running the Platform](#-running-the-platform)
- [Running Automated Tests](#-running-automated-tests)
- [Screenshots & UI Showcase](#-screenshots--ui-showcase)
- [Machine Learning & Backtesting Engine](#-machine-learning--backtesting-engine)
- [Deployment Guide](#-deployment-guide)
- [Known Limitations & Future Roadmap](#-known-limitations--future-roadmap)
- [Statutory Disclaimer](#-statutory-disclaimer)
- [License](#-license)

---

## 🌟 Overview & Core Value

**Listview** is a self-hosted financial intelligence and market analytics platform tailored specifically for the Indian equity and primary market ecosystem (NSE & BSE).

Unlike commercial market platforms that require expensive proprietary API keys, broker subscriptions (e.g., Zerodha Kite Connect, Bloomberg, Refinitiv), or mandatory cloud databases, Listview operates under a strict **Zero Paid APIs Principle**:
- **₹0 API subscription cost**
- **₹0 API-key requirement**
- **Zero-configuration local database** (runs out-of-the-box on SQLite, with ready PostgreSQL support)
- **Graceful 4-tier data cascade** with local caching and bundled offline fallback datasets.

---

## 🚀 Key Features

| Capability | Description |
|---|---|
| **📊 Equities Catalog & Quotes** | Comprehensive tracking across 2,600+ NSE/BSE securities with live valuation multiples (P/E, P/B, ROE, ROCE, D/E, 52W range). |
| **📈 Interactive TradingView Charts** | Powered by `lightweight-charts`, supporting Candlestick, Line, Area, Volume bars, technical overlays (SMA-20, EMA-50), and horizons from `1D` to `5Y`. |
| **🎯 IPO Intelligence Hub** | Complete tracking of Mainboard & SME IPOs: timeline dates, price bands, lot size, subscription quotas (QIB, NII, Retail), and issue sizes. |
| **🔥 Unofficial GMP Tracker** | Real-time tracking of Grey Market Premium with automated calculations (`Estimated Listing = Upper Band + GMP`), estimated listing gain %, and historical GMP movements. |
| **🤖 Walk-Forward AI Predictions** | TimeSeriesSplit directional probability modeling (RandomForest, GradientBoosting) with ethical safeguards (probabilistic bands, no false promises). |
| **🛡️ 10-Pillar Health Score** | Transparent fundamental scoring auditing Revenue Growth, Profit Growth, ROE, ROCE, D/E, EBITDA Margin, Free Cash Flow, Valuation, Liquidity, and Promoter Holding. |
| **🔍 Multi-Factor Stock Screener** | Dynamic screener with real-time filtering across valuation ratios, returns, debt levels, and compounder presets. |
| **💼 Virtual Portfolio Sandbox** | Paper trading simulator with position management, unrealized/realized P&L calculations, and sector allocation breakdown. |
| **🧪 Quantitative Strategy Backtester**| Simulation engine for technical trading strategies (SMA Crossover, EMA Breakout, RSI Reversal, MACD, Momentum) with equity curves and metrics. |
| **⚖️ Comparative Analysis** | Side-by-side metric comparisons for both equities and upcoming IPOs. |
| **📰 NLP News Sentiment Feed** | Market headlines paired with open-source linguistic NLP sentiment analysis. |

---

## 🏛️ Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 React 19 Single Page App                     │
│         (Vite • TypeScript • Tailwind CSS • Lucide)          │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON REST API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend Service                     │
│          (Python 3.10+ • Pydantic v2 • SQLAlchemy)          │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│   4-Tier Fallback Cascade    │ │    Analytical Subsystems    │
│  1. Live Community APIs      │ │  • Scikit-Learn Walk-Forward│
│  2. Public Open Datasets     │ │  • Quantitative Backtester  │
│  3. Local Stored Cache       │ │  • 10-Pillar Health Engine  │
│  4. Bundled Offline Data     │ │  • Natural Language NLP     │
└──────────────┬───────────────┘ └─────────────┬───────────────┘
               │                               │
               └───────────────┬───────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Local Persistence Layer (market.db)              │
│       SQLite (Default zero-config) / PostgreSQL (Prod)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Core Framework**: [FastAPI](https://fastapi.tiangolo.com/) `0.110+` (High-performance ASGI API framework)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/) `0.29+`
- **Data Modeling & Validation**: [Pydantic v2](https://docs.pydantic.dev/) `2.7+`
- **ORM & Database**: [SQLAlchemy](https://www.sqlalchemy.org/) `2.0+` with SQLite & PostgreSQL compatibility
- **Data Processing**: [Pandas](https://pandas.pydata.org/) `2.0+`, [NumPy](https://numpy.org/) `1.26+`
- **Machine Learning**: [Scikit-Learn](https://scikit-learn.org/) `1.4+`, [XGBoost](https://xgboost.readthedocs.io/) `2.0+`
- **HTTP & Networking**: [HTTPX](https://www.python-httpx.org/) `0.27+`, [Requests](https://requests.readthedocs.io/) `2.31+`
- **Feed Processing**: [Feedparser](https://feedparser.readthedocs.io/) `6.0+`
- **Testing**: [Pytest](https://docs.pytest.org/) `8.x` with AnyIO

### Frontend
- **Library**: [React 19](https://react.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/) `5.x`
- **Build Tool**: [Vite 8](https://vitejs.dev/)
- **Styling**: [Tailwind CSS 3.4](https://tailwindcss.com/) with PostCSS & Autoprefixer
- **Financial Charting**: [TradingView Lightweight Charts 5.2](https://github.com/tradingview/lightweight-charts) (Apache-2.0)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Routing**: [React Router v7](https://reactrouter.com/)
- **HTTP Client**: [Axios](https://axios-http.com/)

---

## 🆓 Zero Paid APIs & Data Attribution

Listview is built using transparent, publicly accessible data sources:

1. **Indian Stock Market Community API**:
   - Quotes, Master Securities, Search: [0xramm/Indian-Stock-Market-API](https://github.com/0xramm/Indian-Stock-Market-API) (MIT License).
2. **India IPO GMP Dataset**:
   - Machine-Readable Daily GMP Records: [Spectrumz00/india-ipo-gmp-data](https://github.com/Spectrumz00/india-ipo-gmp-data) (CC BY 4.0 License).
3. **Official NSE Securities Master**:
   - NSE Equity master catalog compiled from official exchange disclosures (`EQUITY_L.csv`).
4. **Offline Bundled Datasets (`demo-data/`)**:
   - Bundled CSVs and JSONs providing full offline fallback when external connections are unavailable.

---

## 📋 Prerequisites & Requirements

- **Python**: Version `3.10` or higher (tested on Python 3.11)
- **Node.js**: Version `18.x`, `20.x`, or `22.x`
- **Package Managers**: `pip` (Python) and `npm` (Node.js)
- **Operating System**: Windows 10/11, macOS, or Ubuntu/Debian Linux

---

## 💻 Local Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/rishikesh807507/listview.git
cd listview
```

### 2. Backend Setup
Create a virtual environment (recommended) and install backend dependencies:

```bash
# Create and activate Python virtual environment
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Database Initialization & Seeding
Initialize the SQLite database (`market.db`) and populate master securities and pricing:

```bash
# 1. Seed base demo tables (stocks, IPOs, GMP, financials, subscriptions)
python seed_database.py

# 2. Load complete NSE official equities master list
python load_securities_master.py

# 3. Enrich top market leaders with complete pricing & fundamental multiples
python enrich_stocks_data.py
```

### 4. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node modules
npm install

# Return to project root
cd ..
```

---

## ⚙️ Configuration (.env.example)

The repository provides [.env.example](.env.example) with safe default values. Create your local `.env` if custom endpoints or databases are needed:

```bash
cp .env.example .env
```

| Variable | Default Value | Description |
|---|---|---|
| `HOST` | `127.0.0.1` | Backend binding IP |
| `PORT` | `8000` | Backend port |
| `DATABASE_URL` | `sqlite:///./market.db` | Database connection string (SQLite or PostgreSQL) |
| `INDIAN_STOCK_API_BASE` | `https://indian-stock-market-api.fly.dev` | Community stock API endpoint |
| `GMP_GITHUB_RAW_URL` | `https://raw.githubusercontent.com/...` | Raw JSON feed for daily GMP |
| `CACHE_EXPIRY_SECONDS` | `300` | Local cache TTL in seconds |
| `VITE_API_BASE_URL` | `/api` | Frontend proxy path to backend API |

---

## 🚀 Running the Platform

### Start Backend API Server
```bash
# From project root:
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative ReDoc UI: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Start Frontend Client
```bash
# In a separate terminal, navigate to frontend:
cd frontend
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Running Automated Tests

The test suite validates database schemas, API routers, calculation formulas, ML prediction limits, and platform endpoints:

```bash
# Run complete test suite (28 tests across test_ipo_module.py and test_platform.py)
python -m pytest test_platform.py test_ipo_module.py -v
```

**Test Verification Summary:**
```text
test_ipo_module.py::test_ipo_endpoints PASSED
test_ipo_module.py::test_gmp_endpoints PASSED
test_ipo_module.py::test_ipo_calculator PASSED
test_ipo_module.py::test_csv_import PASSED
test_platform.py::test_market_overview PASSED
test_platform.py::test_stocks_list PASSED
test_platform.py::test_health_score PASSED
test_platform.py::test_backtest_strategy PASSED
======================= 28 passed in 19.64s =======================
```

---

## 📸 Screenshots & UI Showcase

| Screen | Preview / Description |
|---|---|
| **Market Dashboard** | *Real-time Nifty 50, Sensex indices, market advance-decline ratio, top gainers/losers, active volume radar.* |
| **Interactive Charting** | *TradingView candlestick and volume histogram with SMA-20 / EMA-50 overlays and custom timeframes.* |
| **Stocks Catalog** | *Searchable directory of 2,600+ equities filtered by 12 sectors with real-time pricing and valuation multiples.* |
| **IPO & GMP Tracker** | *Mainboard and SME IPO radar with Grey Market Premium, listing gain estimates, and timeline progress.* |
| **10-Pillar Health Score** | *Detailed corporate fundamentals audit across profitability, solvency, cash generation, and valuation.* |
| **Strategy Backtester** | *Quantitative strategy simulation with cumulative equity curves, win rate, maximum drawdown, and Sharpe ratio.* |

*(UI screenshots can be captured directly from your local browser at `http://localhost:5173`)*

---

## 🤖 Machine Learning & Backtesting Engine

### Walk-Forward Directional Model
- **Algorithm**: `RandomForestClassifier` and `GradientBoostingRegressor` from Scikit-Learn.
- **Lookahead Prevention**: Employs `TimeSeriesSplit` chronological walk-forward cross-validation. Never uses random shuffling.
- **Engineered Features**:
  - RSI (14-period relative strength)
  - MACD (12, 26, 9) and histogram
  - Bollinger Bands position (20-day, 2σ)
  - 1-day and 5-day historical returns
  - 20-day annualized rolling volatility
  - Volume expansion ratio relative to 20-day SMA
- **Outputs**: Directional upside probability %, expected return band, walk-forward accuracy, precision, and confidence metrics.

### Quantitative Strategy Simulation
- **Supported Strategies**: Simple Moving Average Crossover (SMA), Exponential Moving Average (EMA), RSI Mean Reversion, MACD Signal Cross, Momentum Breakout.
- **Metrics Calculated**: Total Return %, Benchmark Return %, Annualized Volatility, Maximum Drawdown (MDD), Win Rate %, Total Trades Executed.

---

## 🚢 Deployment Guide

### Option 1: Linux VM / VPS (Systemd + Nginx)
1. **Backend**: Run Uvicorn managed by systemd or Supervisor on port `8000`.
2. **Frontend**: Build production bundle via `npm run build` inside `frontend/` and serve static assets via Nginx.
3. **Reverse Proxy**: Configure Nginx to route `/api/*` to `http://127.0.0.1:8000/api/*`.

### Option 2: Docker Containerization
```dockerfile
# Multi-stage Dockerfile pattern supported:
# Stage 1: Build React static assets with Vite
# Stage 2: Python 3.11-slim container with FastAPI + Uvicorn serving static files
```

### Option 3: Production Database Migration
To switch from SQLite to PostgreSQL:
```bash
# Update DATABASE_URL in .env:
DATABASE_URL=postgresql://user:password@localhost:5432/listview

# Run migrations/seed:
python seed_database.py
python enrich_stocks_data.py
```

---

## ⚠️ Known Limitations & Future Roadmap

- **Market Session Hours**: External community feeds operate on delayed snapshots outside official NSE market trading hours (09:15 to 15:30 IST).
- **GMP Volatility**: Grey Market Premium data reflects unofficial street sentiment and carries no regulatory backing.
- **Single-Machine Rate Limits**: Public open-source endpoints may rate-limit high-frequency polling; local SQLite caching mitigates this.
- **Future Roadmap**:
  - WebSocket support for sub-second quote streaming during market hours.
  - Options chain analysis (NSE Nifty/BankNifty Open Interest PCR).
  - Mutual Fund portfolio overlap tool.

---

## 📜 Statutory Disclaimer

> **MANDATORY STATUTORY NOTICE:**  
> This platform is developed strictly for **educational, analytical, and informational purposes**.  
> - None of the content, scores, indicators, or machine learning forecasts constitute financial, investment, legal, or trading advice.  
> - Stock market investments are subject to market risks. Read all scheme and offer documents carefully before investing.  
> - Grey Market Premium (GMP) is an unofficial, unregulated, and non-binding indicator and should never be the sole basis for IPO investment decisions.

---

## 📄 License & Attribution

- Platform source code is released under the **[MIT License](LICENSE)**.
- **TradingView Lightweight Charts**: Apache-2.0 License ([GitHub](https://github.com/tradingview/lightweight-charts))
- **Indian Stock Market Community API**: MIT License ([GitHub](https://github.com/0xramm/Indian-Stock-Market-API))
- **India IPO GMP Dataset**: CC BY 4.0 License ([GitHub](https://github.com/Spectrumz00/india-ipo-gmp-data))
