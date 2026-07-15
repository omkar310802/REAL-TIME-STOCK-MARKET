# StockIntel — Real-Time Stock Market Intelligence Dashboard

A full-stack Python/Flask web application for monitoring Indian stock market data with
portfolio tracking, price alerts, analytics charts, and buy/sell/hold signals.

---

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Backend     | Python 3.10+, Flask               |
| Database    | SQLite (via Flask-SQLAlchemy)      |
| Frontend    | HTML5, CSS3, JavaScript (ES6+)    |
| Charts      | Chart.js 4.4                      |
| Auth        | Werkzeug password hashing         |
| Fonts       | DM Sans + JetBrains Mono (Google) |

---

## Project Structure

```
stock_dashboard/
├── app.py                  ← Flask application + API routes + DB models
├── requirements.txt        ← Python dependencies
├── README.md
├── templates/
│   ├── login.html          ← Login page
│   ├── register.html       ← Registration page
│   └── dashboard.html      ← Main dashboard (all tabs)
└── static/
    ├── css/
    │   └── dashboard.css   ← Dark theme stylesheet
    └── js/
        └── dashboard.js    ← All frontend logic, charts, API calls
```

---

## Setup & Run

### 1. Install Python dependencies

```bash
cd stock_dashboard
pip install -r requirements.txt
```

### 2. Run the application

```bash
python app.py
```

### 3. Open in browser

```
http://localhost:5000
```

- Register a new account, then log in.
- The database (`stockintel.db`) is created automatically on first run.

---

## Features

### Market Overview
- Live simulated prices for 15 NSE stocks in Indian Rupees (₹)
- Nifty 50 and Sensex index display
- Buy / Sell / Hold signals per stock
- Interactive price history charts (1D / 1W / 1M / 3M)
- Sortable watchlist table with 52-week High/Low

### Portfolio Tracker
- Add holdings with ticker, quantity, and buy price
- Real-time P&L calculation per holding and overall
- Total invested vs current value summary

### Price Alerts
- Set "price above" or "price below" alerts
- Automatic status (Active / Triggered) based on current price
- Per-user alert storage in SQLite

### Analytics
- Sector-wise performance bar chart
- Portfolio sector diversification donut chart
- Top gainers vs losers comparison chart

---

## Connecting Real Live Data (Optional)

To replace simulated prices with real NSE/BSE data, install `yfinance`:

```bash
pip install yfinance
```

Then replace the `get_live_price()` function in `app.py`:

```python
import yfinance as yf

def get_live_price(ticker):
    stock = yf.Ticker(ticker + ".NS")   # .NS for NSE
    info  = stock.fast_info
    return {
        'ticker':     ticker,
        'price':      round(info.last_price, 2),
        'change':     round(info.last_price - info.previous_close, 2),
        'change_pct': round(((info.last_price - info.previous_close) / info.previous_close) * 100, 2),
        ...
    }
```

---

## Screenshots

- Dark terminal-style theme with green accent colors
- Sidebar navigation with user avatar
- Responsive tables with sortable columns
- Modal pop-up for detailed stock view
- Toast notifications for user actions

---

## Author

Built for: Real-Time Stock Market Intelligence Dashboard (MCA Project)
Department of MCA, SSIT, Tumakuru — 2025-26
