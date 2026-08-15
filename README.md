# Smart-Stock-Screener

A Python-based quantitative stock screening tool that fetches live financial data from **Yahoo Finance** to identify high-performing S&P 500 equities. The program combines relative strength momentum, trend alignment, and fundamental valuation metrics based on Mark Minervini's Trend Template principles.

---

## Key Features

* **Automated Data Ingestion:** Scrapes the current S&P 500 constituent list from Wikipedia and pulls historical market data directly from **Yahoo Finance** using `yfinance`.
* **Relative Strength Ranking:** Benchmarks each individual stock's 1-year cumulative performance against the S&P 500 index (`^GSPC`) to isolate market leaders.
* **Moving Average Trend Analysis:** Calculates 150-day and 200-day Simple Moving Averages (SMA) to confirm structural uptrends.
* **Breakout & Range Checks:** Evaluates 52-week price channels to ensure stocks are trading near highs while avoiding overextended setups.
* **Fundamental Valuation Filtering:** Queries trailing P/E and PEG ratios directly from **Yahoo Finance** to filter out overvalued candidates.
* **Local Data Storage:** Exports raw price data for processed tickers to `stock_data/` and saves the final filtered watchlist to `final.csv`.

---

## Screening Criteria

To pass the screen and enter the final watchlist, a stock must meet all five conditions:

| Criterion | Formula / Threshold | Description |
| :--- | :--- | :--- |
| **Momentum** | Top 30% Relative Strength | Outperforms the baseline S&P 500 index over 1 year |
| **Uptrend** | $\text{Price} \gt \text{SMA}_{150} \gt \text{SMA}_{200}$ | Price is in a confirmed, multi-stage uptrend |
| **52-Week Low** | $\text{Price} \ge 1.30 \times \text{Low}_{52\text{W}}$ | Price is at least 30% above its 52-week low |
| **52-Week High**| $\text{Price} \ge 0.75 \times \text{High}_{52\text{W}}$ | Price is within 25% of its 52-week high |
| **Valuation** | $\text{P/E} < 40$ & $\text{PEG} < 2.0$ | Fundamental sanity checks via Yahoo Finance |

---

## Prerequisites

Ensure you have Python 3.9+ installed along with the required third-party libraries:

```bash
pip install pandas yfinance requests lxml html5lib

