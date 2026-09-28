# 📈 Quantitative Stock Trading & Backtesting Simulator 🇨🇦

A comprehensive, interactive financial quantitative backtester built in Python for the **Stanford Code in Place 2026 Final Project Showcase**.

This application allows users to analyze real-world stock market data (such as major Canadian blue chips like Royal Bank of Canada or technology leaders like Shopify), define custom starting capital and monthly contributions, simulate **8 distinct investment and technical trading strategies**, calculate institutional risk-adjusted metrics, visualize execution markers on professional **Candlestick charts**, and evaluate outcomes through an automated **Tournament Leaderboard** and **Market Post-Mortem**.

---

## 🚀 Key Features

1. **Live Financial Data Ingestion**:
   - Downloads historical daily price data (Open, High, Low, Close, Volume) using yfinance.
   - Supports any global ticker symbol (e.g., RY, SHOP, AAPL, MSFT, SPY).

2. **Custom Capital & Cash Flow Management**:
   - Prompts the user for starting capital and planned monthly deposits (simulating real-world TFSA, RRSP, or 401(k) contributions).

3. **8 Quantitative & Technical Trading Strategies**:
   - **Portfolio Allocation & Systematic Strategies**:
     - Buy & Hold: Passive investment benchmark (the classic buy-and-forget).
     - Dollar-Cost Averaging (DCA): Systematic monthly purchases reducing timing risk.
     - Buy the Dip: Mean-reversion buying after consecutive dips, taking profit at +5%.
     - Risk-Managed Stop Loss: Long position with an automated -7% capital preservation stop.
   - **Technical & Charting Strategies**:
     - Support & Resistance Breakout: Buys on 20-day High breakouts; sells on 20-day Low breakdowns.
     - Moving Average Crossover: The classic Golden Cross (SMA 20 crossing above SMA 50).
     - Bollinger Bands Reversion: Volatility envelope trading (buys lower band, sells upper band).
     - RSI Momentum: Relative Strength Index oscillation triggers (Oversold < 30, Overbought > 70).

4. **Institutional Risk & Performance Metrics (DAMO611 Standards)**:
   - Net Profit ($ and %)
   - Daily & Annualized Stock Volatility ($\sigma \times \sqrt{252}$)
   - Sharpe Ratio (Risk-adjusted return)
   - Maximum Drawdown (% peak-to-trough decline)
   - Trade execution count

5. **Strategy Tournament Leaderboard & Automated Market Post-Mortem**:
   - Simulates all 8 strategies simultaneously in the background.
   - Ranks all strategies from 1st to 8th place by performance.
   - Automatically diagnoses **WHY** the winning strategy won based on the underlying market regime (Bull Market, Bear Market, or Range-Bound Choppy Market).

6. **Interactive Candlestick Visualizations (mplfinance)**:
   - Displays real Green (Bullish) and Red (Bearish) Japanese Candlesticks with volume.
   - Overlays technical indicator lines (Support/Resistance, Moving Averages).
   - Plots execution markers directly onto candles: Green Triangles (▲) for Buys, Red Triangles (▼) for Sells.

---

## 🛠️ Installation & Setup

1. **Clone the repository**:
   `ash
   git clone https://github.com/Adrian-Eng-Br/quantitative-trading-backtester.git
   cd quantitative-trading-backtester
   `

2. **Install dependencies**:
   `ash
   pip install yfinance mplfinance pandas numpy matplotlib
   `

3. **Run the application**:
   `ash
   python main.py
   `
   *Or run the interactive notebook: Financial_test.ipynb in Jupyter Notebook / VS Code.*

---

## 📊 Sample Output (Executive Summary & Leaderboard)

`	ext
====================================================================
         EXECUTIVE PERFORMANCE REPORT: RY (Royal Bank of Canada)         
====================================================================
Selected Strategy:     Support & Resistance Breakout
Total Invested:        ,800.00
Final Portfolio Value: ,693.21
Net Profit / Loss:     +.21 (+31.90%)
--------------------------------------------------------------------
--- STOCK RISK METRICS (DAMO611 STANDARDS) ---
Daily Stock Volatility:      1.18% per day
Annualized Stock Volatility: 18.73% per year
Strategy Sharpe Ratio:       3.15
Max Portfolio Drawdown:      6.39%
Total Trades Executed:       14
--------------------------------------------------------------------
=================== STRATEGY TOURNAMENT LEADERBOARD ===================
Rank Strategy                            Return (%)    Final Value ($)
--------------------------------------------------------------------
1 🏆 Buy & Hold (Passive Benchmark)        +68.68%        ,723.04
2    Moving Average Crossover (SMA 20/50)  +42.15%        ,980.20
3 👉 Support & Resistance Breakout (Yours) +31.90%        ,693.21
4    Bollinger Bands Reversion             +24.10%        ,474.80
...
====================================================================
`

---

## 👤 Author
- **Adrian Aguilera**
- Master of Data Analytics Student | University of Niagara Falls Canada
- LinkedIn: [linkedin.com/in/adrianaguilera](https://www.linkedin.com/in/adrian-aguilera-/)
- GitHub: [github.com/Adrian-Eng-Br](https://github.com/Adrian-Eng-Br)

*Created for Stanford University's Code in Place 2026 Program.*
