import numpy as np
import pandas as pd
from typing import Dict, Any, List

def run_backtest(prices: List[Dict[str, Any]], strategy: str = "SMA", initial_capital: float = 100000.0, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Simulates trading strategies on chronological historical OHLCV data.
    Clearly labeled as 'Historical Simulation Only'.
    """
    if len(prices) < 30:
        return {"error": "At least 30 trading candles required for backtesting."}

    df = pd.DataFrame(prices)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    params = params or {}
    
    # Generate signals
    df['signal'] = 0  # 1 = Buy/Hold, 0 = Cash
    
    if strategy == "SMA":
        fast = int(params.get("fast_period", 10))
        slow = int(params.get("slow_period", 30))
        df['fast_ma'] = df['close'].rolling(fast).mean()
        df['slow_ma'] = df['close'].rolling(slow).mean()
        df.loc[df['fast_ma'] > df['slow_ma'], 'signal'] = 1

    elif strategy == "EMA":
        fast = int(params.get("fast_period", 9))
        slow = int(params.get("slow_period", 21))
        df['fast_ema'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['slow_ema'] = df['close'].ewm(span=slow, adjust=False).mean()
        df.loc[df['fast_ema'] > df['slow_ema'], 'signal'] = 1

    elif strategy == "RSI":
        oversold = float(params.get("oversold", 35.0))
        overbought = float(params.get("overbought", 65.0))
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss.replace(0, np.nan))
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # In position when RSI crosses above oversold, exit when above overbought
        in_pos = 0
        signals = []
        for rsi in df['rsi']:
            if rsi < oversold:
                in_pos = 1
            elif rsi > overbought:
                in_pos = 0
            signals.append(in_pos)
        df['signal'] = signals

    elif strategy == "MACD":
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal_line = macd.ewm(span=9, adjust=False).mean()
        df.loc[macd > signal_line, 'signal'] = 1

    else:  # Momentum (Price > 20-day high or positive 20-day return)
        lookback = int(params.get("lookback", 20))
        df['momentum'] = df['close'].pct_change(lookback)
        df.loc[df['momentum'] > 0.02, 'signal'] = 1

    # Shift signal by 1 day to execute at next day's open/close (prevent same-day lookahead)
    df['exec_signal'] = df['signal'].shift(1).fillna(0)
    
    # Portfolio simulation
    capital = initial_capital
    position = 0
    buy_price = 0.0
    trades = []
    equity_curve = []
    
    peak_capital = initial_capital
    max_drawdown = 0.0
    
    for i, row in df.iterrows():
        current_price = row['close']
        dt_str = row['timestamp'].strftime("%Y-%m-%d")
        sig = row['exec_signal']
        
        # Entry
        if sig == 1 and position == 0:
            position = int(capital / current_price)
            if position > 0:
                buy_price = current_price
                capital -= position * current_price
                trades.append({
                    "type": "BUY",
                    "date": dt_str,
                    "price": round(buy_price, 2),
                    "quantity": position,
                    "capital_remaining": round(capital, 2)
                })
        
        # Exit
        elif sig == 0 and position > 0:
            sell_price = current_price
            pnl = (sell_price - buy_price) * position
            pnl_pct = round(((sell_price - buy_price) / buy_price) * 100, 2)
            capital += position * sell_price
            trades.append({
                "type": "SELL",
                "date": dt_str,
                "price": round(sell_price, 2),
                "quantity": position,
                "pnl": round(pnl, 2),
                "pnl_percent": pnl_pct,
                "capital_after": round(capital, 2)
            })
            position = 0
            buy_price = 0.0
            
        current_equity = capital + (position * current_price)
        peak_capital = max(peak_capital, current_equity)
        dd = (peak_capital - current_equity) / peak_capital * 100
        max_drawdown = max(max_drawdown, dd)
        
        equity_curve.append({
            "date": dt_str,
            "equity": round(current_equity, 2),
            "benchmark": round(initial_capital * (current_price / df.iloc[0]['close']), 2)
        })

    # If position still open at the end
    final_equity = capital + (position * df.iloc[-1]['close'])
    if position > 0:
        trades.append({
            "type": "HOLDING_AT_END",
            "date": df.iloc[-1]['timestamp'].strftime("%Y-%m-%d"),
            "price": round(df.iloc[-1]['close'], 2),
            "quantity": position,
            "unrealized_pnl": round((df.iloc[-1]['close'] - buy_price) * position, 2)
        })

    # Trade stats
    completed_sells = [t for t in trades if t["type"] == "SELL"]
    winning_trades = len([t for t in completed_sells if t.get("pnl", 0) > 0])
    total_completed = len(completed_sells)
    win_rate = round((winning_trades / total_completed * 100), 1) if total_completed > 0 else 0.0
    
    total_return_pct = round(((final_equity - initial_capital) / initial_capital) * 100, 2)
    benchmark_return_pct = round(((df.iloc[-1]['close'] - df.iloc[0]['close']) / df.iloc[0]['close']) * 100, 2)

    return {
        "strategy": strategy,
        "initial_capital": initial_capital,
        "final_capital": round(final_equity, 2),
        "return_percent": total_return_pct,
        "benchmark_return": benchmark_return_pct,
        "max_drawdown": round(max_drawdown, 2),
        "total_trades": len(trades),
        "completed_trades": total_completed,
        "winning_trades": winning_trades,
        "win_rate": win_rate,
        "trades": trades,
        "equity_curve": equity_curve[-60:],  # last 60 points for neat charting
        "label": "Historical Simulation Only — Past performance is never indicative of future returns"
    }
