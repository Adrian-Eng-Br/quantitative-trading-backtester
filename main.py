"""
File: main.py
---------------------------------------------------------------
Quantitative Stock Trading & Investment Backtester
Author: Adrian Aguilera
Institution: University of Niagara Falls Canada / Code in Place 2026
---------------------------------------------------------------
Simulates 8 distinct investment and technical trading strategies
on real-world historical market data, calculates institutional
risk-adjusted metrics (Sharpe Ratio, Volatility, Drawdown),
renders Candlestick charts with Buy/Sell markers, and provides
an automated Tournament Leaderboard with Market Post-Mortem.
"""

import math
import numpy as np
import pandas as pd
import yfinance as yf
import mplfinance as mpf


# ==========================================
# 1. DATA INGESTION & LOADING
# ==========================================

def download_stock_data():
    """
    Prompts the user for a stock ticker symbol and time period,
    downloads the historical data from Yahoo Finance, and saves it to a CSV file.
    """
    print("=== STOCK DATA DOWNLOADER ===")
    print("Popular ticker examples:")
    print("- RY    (Royal Bank of Canada)")
    print("- SHOP  (Shopify)")
    print("- AAPL  (Apple)")
    print("- MSFT  (Microsoft)")
    print("- SPY   (S&P 500 ETF)")
    print("-----------------------------")
    
    ticker = input("Enter the stock ticker symbol to analyze: ").strip().upper()
    if ticker == "":
        ticker = "RY"
        
    period = input("Enter time period (e.g., 1y, 2y, 5y) [Press Enter for 2y]: ").strip()
    if period == "":
        period = "2y"
        
    print(f"\nDownloading historical data for {ticker} over {period}...")
    stock_df = yf.download(ticker, period=period)
    
    if stock_df.empty:
        print(f"❌ Error: Could not find data for ticker '{ticker}'.")
        return None
        
    filename = f"{ticker}.csv"
    stock_df.to_csv(filename)
    print(f"✅ Success! Data saved to: {filename}")
    return filename


def load_prices(filename):
    """
    Reads a CSV file and extracts the Date and the Closing Price for each day.
    Returns a list of dictionaries: [{'date': '2024-09-18', 'price': 284.93}, ...]
    """
    price_history = []
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines[1:]:
            parts = line.strip().split(",")
            if len(parts) >= 2 and parts[1] != "":
                try:
                    date = parts[0]
                    price = float(parts[1])
                    price_history.append({"date": date, "price": price})
                except ValueError:
                    continue
    return price_history


def get_user_investment_params():
    """
    Prompts the user for initial starting capital and monthly contribution.
    """
    print("\n=== INVESTMENT CAPITAL & CONTRIBUTIONS ===")
    init_in = input("Enter initial starting capital ($) [Default: 10000]: ").strip()
    initial_capital = float(init_in) if init_in != "" else 10000.0
    
    contrib_in = input("Enter planned monthly contribution ($) [Default: 500]: ").strip()
    monthly_contribution = float(contrib_in) if contrib_in != "" else 500.0
    
    print(f"💰 Starting Capital: ${initial_capital:,.2f} | Monthly Deposit: ${monthly_contribution:,.2f}\n")
    return initial_capital, monthly_contribution


# ==========================================
# 2. MATHEMATICAL INDICATORS ENGINE
# ==========================================

def calculate_sma(prices, window):
    """Calculates Simple Moving Average for a given window."""
    sma = []
    for i in range(len(prices)):
        if i < window - 1:
            sma.append(None)
        else:
            subset = prices[i - window + 1 : i + 1]
            sma.append(sum(subset) / window)
    return sma


def calculate_support_resistance(prices, window=20):
    """Calculates rolling 20-day high (resistance) and 20-day low (support)."""
    resistances, supports = [], []
    for i in range(len(prices)):
        if i < window:
            resistances.append(None)
            supports.append(None)
        else:
            subset = prices[i - window : i]
            resistances.append(max(subset))
            supports.append(min(subset))
    return resistances, supports


def calculate_bollinger_bands(prices, window=20, num_std=2):
    """Calculates Bollinger Bands (Middle, Upper, Lower)."""
    sma = calculate_sma(prices, window)
    upper_band, lower_band = [], []
    for i in range(len(prices)):
        if sma[i] is None:
            upper_band.append(None)
            lower_band.append(None)
        else:
            subset = prices[i - window + 1 : i + 1]
            mean = sma[i]
            variance = sum((x - mean) ** 2 for x in subset) / window
            std_dev = math.sqrt(variance)
            upper_band.append(mean + (num_std * std_dev))
            lower_band.append(mean - (num_std * std_dev))
    return sma, upper_band, lower_band


def calculate_rsi(prices, period=14):
    """Calculates Relative Strength Index (RSI 14)."""
    rsi = [None] * len(prices)
    if len(prices) <= period:
        return rsi
        
    gains, losses = [], []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))
        
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        rsi[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi[period] = 100.0 - (100.0 / (1.0 + rs))
        
    for i in range(period + 1, len(prices)):
        change = prices[i] - prices[i - 1]
        gain = max(change, 0.0)
        loss = max(-change, 0.0)
        
        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period
        
        if avg_loss == 0:
            rsi[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[i] = 100.0 - (100.0 / (1.0 + rs))
            
    return rsi


# ==========================================
# 3. BACKTEST SIMULATION ENGINE
# ==========================================

def run_backtest(history, strategy_id, initial_capital, monthly_contribution):
    """
    Simulates the selected trading strategy across the historical data
    using custom user capital and monthly contribution.
    """
    prices = [day["price"] for day in history]
    dates = [day["date"] for day in history]

    sma20 = calculate_sma(prices, 20)
    sma50 = calculate_sma(prices, 50)
    resistances, supports = calculate_support_resistance(prices, 20)
    _, upper_band, lower_band = calculate_bollinger_bands(prices, 20, 2)
    rsi14 = calculate_rsi(prices, 14)

    cash = initial_capital
    shares = 0.0
    total_invested = initial_capital
    trades = []
    portfolio_values = []
    entry_price = 0.0

    for i in range(len(prices)):
        current_price = prices[i]
        current_date = dates[i]

        if i > 0 and i % 21 == 0 and monthly_contribution > 0:
            cash += monthly_contribution
            total_invested += monthly_contribution
        
        buy_signal = False
        sell_signal = False
        
        if strategy_id == 1:  # Buy & Hold
            if cash > 0:
                buy_signal = True
        
        elif strategy_id == 2:  # Dollar-Cost Averaging (DCA)
            if cash > 0 and (i == 0 or i % 21 == 0):
                buy_signal = True
                
        elif strategy_id == 3:  # Buy the Dip
            if i >= 2 and prices[i] < prices[i - 1] < prices[i - 2] and cash > 0 and shares == 0:
                buy_signal = True
            elif shares > 0 and current_price >= entry_price * 1.05:
                sell_signal = True

        elif strategy_id == 4:  # Stop Loss (-7%)
            if i == 0 and cash > 0:
                buy_signal = True
            elif shares > 0 and current_price <= entry_price * 0.93:
                sell_signal = True 

        elif strategy_id == 5:  # Support & Resistance Breakout
            if resistances[i] is not None and supports[i] is not None:
                if current_price > resistances[i] and cash > 0 and shares == 0:
                    buy_signal = True 
                elif current_price < supports[i] and shares > 0:
                    sell_signal = True
                
        elif strategy_id == 6:  # Moving Average Crossover (SMA 20/50)
            if sma20[i] is not None and sma50[i] is not None and sma20[i - 1] is not None and sma50[i - 1] is not None:
                if sma20[i] > sma50[i] and sma20[i - 1] <= sma50[i - 1] and cash > 0 and shares == 0:
                    buy_signal = True
                elif sma20[i] < sma50[i] and sma20[i - 1] >= sma50[i - 1] and shares > 0:
                    sell_signal = True

        elif strategy_id == 7:  # Bollinger Bands Reversion
            if lower_band[i] is not None and upper_band[i] is not None:
                if current_price <= lower_band[i] and cash > 0 and shares == 0:
                    buy_signal = True
                elif current_price >= upper_band[i] and shares > 0:
                    sell_signal = True
        
        elif strategy_id == 8:  # RSI (30/70)
            if rsi14[i] is not None:
                if rsi14[i] < 30 and cash > 0 and shares == 0:
                    buy_signal = True
                elif rsi14[i] > 70 and shares > 0:
                    sell_signal = True

        if buy_signal and cash > 0: 
            bought_shares = cash / current_price
            shares += bought_shares
            entry_price = current_price
            trades.append({"date": current_date, "type": "BUY", "price": current_price, "shares": bought_shares, "index": i})
            cash = 0.0

        elif sell_signal and shares > 0:
            cash += shares * current_price
            trades.append({"date": current_date, "type": "SELL", "price": current_price, "shares": shares, "index": i})
            shares = 0.0
            entry_price = 0.0

        current_total_value = cash + (shares * current_price)
        portfolio_values.append(current_total_value)

    return {
        "final_value": portfolio_values[-1],
        "total_invested": total_invested,
        "portfolio_values": portfolio_values,
        "trades": trades,
        "prices": prices,
        "dates": dates,
        "indicators": {
            "sma20": sma20, "sma50": sma50,
            "resistances": resistances, "supports": supports,
            "upper_band": upper_band, "lower_band": lower_band,
            "rsi14": rsi14
        }
    }


# ==========================================
# 4. INSTITUTIONAL PERFORMANCE METRICS
# ==========================================

def calculate_performance_metrics(results, risk_free_rate=0.03):
    """Computes financial metrics with Stock Price Volatility (DAMO611 standards)."""
    portfolio_values = results["portfolio_values"]
    total_invested = results["total_invested"]
    final_val = results["final_value"]
    prices = results["prices"]
    
    net_profit = final_val - total_invested
    total_return_pct = (net_profit / total_invested) * 100.0
    
    stock_daily_returns = []
    for i in range(1, len(prices)):
        prev_p = prices[i - 1]
        if prev_p > 0:
            stock_daily_returns.append((prices[i] - prev_p) / prev_p)
            
    if len(stock_daily_returns) > 1:
        mean_return = sum(stock_daily_returns) / len(stock_daily_returns)
        variance = sum((r - mean_return) ** 2 for r in stock_daily_returns) / (len(stock_daily_returns) - 1)
        daily_volatility = math.sqrt(variance)
        annualized_volatility = daily_volatility * math.sqrt(252)
    else:
        daily_volatility, annualized_volatility = 0.0, 0.0
        
    strategy_daily_ret = []
    for i in range(1, len(portfolio_values)):
        pv = portfolio_values[i - 1]
        strategy_daily_ret.append((portfolio_values[i] - pv) / pv if pv > 0 else 0)
        
    strat_mean = sum(strategy_daily_ret) / len(strategy_daily_ret) if strategy_daily_ret else 0
    strat_var = sum((r - strat_mean) ** 2 for r in strategy_daily_ret) / (len(strategy_daily_ret) - 1) if len(strategy_daily_ret) > 1 else 0
    strat_vol = math.sqrt(strat_var) * math.sqrt(252)
    
    sharpe_ratio = ((strat_mean * 252) - risk_free_rate) / strat_vol if strat_vol > 0 else 0.0
    
    max_peak = portfolio_values[0]
    max_drawdown = 0.0
    for val in portfolio_values:
        if val > max_peak:
            max_peak = val
        drawdown = (max_peak - val) / max_peak if max_peak > 0 else 0
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            
    return {
        "net_profit": net_profit,
        "total_return_pct": total_return_pct,
        "daily_stock_volatility": daily_volatility * 100.0,
        "annualized_stock_volatility": annualized_volatility * 100.0,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown_pct": max_drawdown * 100.0,
        "total_trades": len(results["trades"])
    }


# ==========================================
# 5. CANDLESTICK VISUALIZATION
# ==========================================

def plot_simulation_results(results, strategy_name, ticker_name):
    """
    Renders professional Green/Red Candlesticks with all Buy/Sell signals,
    Support & Resistance lines, and an audit of trades.
    """
    filename = f"{ticker_name}.csv"
    try:
        df = pd.read_csv(filename, skiprows=2)
        df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
    except Exception:
        df = pd.read_csv(filename)
        
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    
    total_buys = sum(1 for t in results["trades"] if t["type"] == "BUY")
    total_sells = sum(1 for t in results["trades"] if t["type"] == "SELL")
    
    buy_signals = [np.nan] * len(df)
    sell_signals = [np.nan] * len(df)
    
    for t in results["trades"]:
        trade_idx = t["index"]
        if trade_idx < len(df):
            if t["type"] == "BUY":
                buy_signals[trade_idx] = df["Low"].iloc[trade_idx] * 0.985
            elif t["type"] == "SELL":
                sell_signals[trade_idx] = df["High"].iloc[trade_idx] * 1.015

    plots = []
    if any(~np.isnan(buy_signals)):
        plots.append(mpf.make_addplot(buy_signals, type='scatter', marker='^', markersize=140, color='#00FF66'))
    if any(~np.isnan(sell_signals)):
        plots.append(mpf.make_addplot(sell_signals, type='scatter', marker='v', markersize=140, color='#FF3366'))
        
    indicators = results["indicators"]
    if ("Support" in strategy_name or "Breakout" in strategy_name) and len(indicators["resistances"]) == len(df):
        res_line = [r if r is not None else np.nan for r in indicators["resistances"]]
        sup_line = [s if s is not None else np.nan for s in indicators["supports"]]
        plots.append(mpf.make_addplot(res_line, color='#26a69a', linestyle='--', width=1.2))
        plots.append(mpf.make_addplot(sup_line, color='#ef5350', linestyle='--', width=1.2))

    binance_style = mpf.make_mpf_style(base_mpf_style='binancedark', rc={'font.size': 10})
    
    print("\n" + "=" * 68)
    print(f"📊 TRADE AUDIT & STRATEGY EXECUTION SUMMARY: {ticker_name}")
    print("=" * 68)
    print(f"• Strategy Applied:      {strategy_name}")
    print(f"• Total BUY Signals (▲): {total_buys} operations")
    print(f"• Total SELL Signals (▼): {total_sells} operations")
    print("=" * 68 + "\n")
    
    mpf.plot(
        df,
        type='candle',
        style=binance_style,
        title=f"\n{ticker_name} - Candlestick Chart | {strategy_name}\n[▲ Total Buys: {total_buys} | ▼ Total Sells: {total_sells}]",
        ylabel='Price ($)',
        volume=True,
        addplot=plots,
        figratio=(16, 9),
        figscale=1.15
    )


# ==========================================
# 6. MARKET POST-MORTEM & MAIN DRIVER
# ==========================================

def explain_winner(best_strategy_id, ticker_name, prices):
    """Provides an automated post-mortem explaining WHY the winning strategy won."""
    first_p = prices[0]
    last_p = prices[-1]
    overall_stock_trend = ((last_p - first_p) / first_p) * 100.0
    
    print("\n" + "=" * 68)
    print(f"💡 STRATEGY POST-MORTEM: WHY DID THE WINNING STRATEGY WIN? 💡")
    print("=" * 68)
    print(f"Market Environment: {ticker_name} had a total price move of {overall_stock_trend:+.2f}%.")
    
    if best_strategy_id in [1, 2]:
        print("\n📌 Key Driver: PERSISTENT BULL MARKET MOMENTUM")
        print(f"• Because {ticker_name} was in a strong, sustained upward trend, staying 100% invested")
        print("  allowed the investor to capture every leg of the growth without any 'cash drag'.")
        print("• Active strategies that sold during temporary pullbacks missed out on subsequent")
        print("  rallies, proving that in strong bull markets, simple holding beats market timing!")
        
    elif best_strategy_id in [5, 6]:
        print("\n📌 Key Driver: MACRO TREND CAPTURE & NOISE FILTERING")
        print(f"• {ticker_name} exhibited clear, multi-month directional cycles with sharp turning points.")
        print("• Trend-following rules (Moving Averages / Breakouts) successfully stayed in the market")
        print("  during explosive rallies and switched to cash before major corrections took place.")
        print("• This captured high alpha while avoiding the full impact of market drawdowns.")
        
    elif best_strategy_id in [3, 7, 8]:
        print("\n📌 Key Driver: VOLATILITY HARVESTING & MEAN REVERSION")
        print(f"• {ticker_name} had an oscillating, sideways or choppy trajectory (Range-Bound Market).")
        print("• While Buy & Hold struggled with stagnation, mean-reversion rules (RSI/Bollinger/Dip)")
        print("  consistently bought when the asset was oversold and banked profits at overbought peaks.")
        print("• Systematically buying lows and selling highs outperformed passive holding.")
        
    elif best_strategy_id == 4:
        print("\n📌 Key Driver: CAPITAL PRESERVATION IN A BEAR MARKET")
        print(f"• {ticker_name} suffered from deep or persistent declines during this period.")
        print("• The Stop Loss trigger prevented catastrophic portfolio destruction by shifting to cash,")
        print("  protecting hard-earned capital while passive investors held through heavy losses.")
        
    print("=" * 68 + "\n")


def main():
    print("=================================================================")
    print("      QUANTITATIVE TRADING & INVESTMENT BACKTESTER 🇨🇦📈          ")
    print("=================================================================\n")
    
    stock_file = download_stock_data()
    if not stock_file:
        return
        
    ticker_name = stock_file.replace(".csv", "")
    history = load_prices(stock_file)
    print(f"\n✅ Successfully loaded {len(history)} trading days for {ticker_name}.")
    
    initial_capital, monthly_contribution = get_user_investment_params()
    
    strategy_names = {
        1: "Buy & Hold (Passive Benchmark)",
        2: "Dollar-Cost Averaging (Monthly DCA)",
        3: "Buy the Dip (Mean Reversion)",
        4: "Risk-Managed Stop Loss (-7% Stop)",
        5: "Support & Resistance Breakout",
        6: "Moving Average Crossover (SMA 20/50)",
        7: "Bollinger Bands Reversion",
        8: "RSI Momentum (30/70 Levels)"
    }
    
    menu_prompt = (
        "\nSELECT STRATEGY TO ANALYZE (1 to 8):\n"
        "[1] Buy & Hold\n"
        "[2] Monthly DCA\n"
        "[3] Buy the Dip\n"
        "[4] Stop Loss (-7%)\n"
        "[5] Support/Resistance Breakout\n"
        "[6] SMA Crossover (20 vs 50)\n"
        "[7] Bollinger Bands\n"
        "[8] RSI (30/70)\n"
        "Enter number (1-8): "
    )
    
    strategy_id = int(input(menu_prompt).strip())
    if strategy_id not in strategy_names:
        print("❌ Invalid selection.")
        return
        
    chosen_strategy = strategy_names[strategy_id]
    print(f"\n🚀 Running full market simulation across all strategies for {ticker_name}...")
    
    user_results = run_backtest(history, strategy_id, initial_capital, monthly_contribution)
    user_metrics = calculate_performance_metrics(user_results)
    
    leaderboard = []
    for sid, sname in strategy_names.items():
        res = run_backtest(history, sid, initial_capital, monthly_contribution)
        met = calculate_performance_metrics(res)
        leaderboard.append({
            "id": sid, "name": sname,
            "return_pct": met["total_return_pct"],
            "final_value": res["final_value"],
            "sharpe": met["sharpe_ratio"]
        })
        
    leaderboard.sort(key=lambda x: x["return_pct"], reverse=True)
    best_strategy = leaderboard[0]
    
    print("\n" + "=" * 68)
    print(f"         EXECUTIVE PERFORMANCE REPORT: {ticker_name}         ")
    print("=" * 68)
    print(f"Selected Strategy:     {chosen_strategy}")
    print(f"Total Invested:        ${user_results['total_invested']:,.2f}")
    print(f"Final Portfolio Value: ${user_results['final_value']:,.2f}")
    print(f"Net Profit / Loss:     ${user_metrics['net_profit']:,.2f} ({user_metrics['total_return_pct']:+.2f}%)")
    print("-" * 68)
    print("--- STOCK RISK METRICS (DAMO611 MODULE 4) ---")
    print(f"Daily Stock Volatility:      {user_metrics['daily_stock_volatility']:.2f}% per day")
    print(f"Annualized Stock Volatility: {user_metrics['annualized_stock_volatility']:.2f}% per year")
    print(f"Strategy Sharpe Ratio:       {user_metrics['sharpe_ratio']:.2f}")
    print(f"Max Portfolio Drawdown:      {user_metrics['max_drawdown_pct']:.2f}%")
    print(f"Total Trades Executed:       {user_metrics['total_trades']}")
    print("-" * 68)
    
    print("=================== STRATEGY TOURNAMENT LEADERBOARD ===================")
    print(f"{'Rank':<5}{'Strategy':<38}{'Return (%)':<14}{'Final Value ($)':<12}")
    print("-" * 68)
    for rank, item in enumerate(leaderboard, start=1):
        mark = "👉 (Sua)" if item["id"] == strategy_id else ("🏆 (Top)" if rank == 1 else "        ")
        print(f"{rank:<2} {mark:<8} {item['name']:<35} {item['return_pct']:>+8.2f}%     ${item['final_value']:>10,.2f}")
    print("=" * 68)
    print(f"🏆 Best Performing Strategy: {best_strategy['name']} ({best_strategy['return_pct']:+.2f}%)")
    
    stock_prices = [day["price"] for day in history]
    explain_winner(best_strategy["id"], ticker_name, stock_prices)
    
    plot_simulation_results(user_results, chosen_strategy, ticker_name)


if __name__ == "__main__":
    main()
