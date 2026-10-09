import React, { useState } from 'react';
import { PlayCircle, ShieldAlert, TrendingUp, TrendingDown, RefreshCw, BarChart2 } from 'lucide-react';
import { runBacktestSimulation } from '../api/client';
import { SearchableStockSelector } from '../components/SearchableStockSelector';

export const Backtesting: React.FC = () => {
  const [symbol, setSymbol] = useState<string>('RELIANCE');
  const [strategy, setStrategy] = useState<string>('SMA');
  const [capital, setCapital] = useState<number>(100000);
  const [fastPeriod, setFastPeriod] = useState<number>(10);
  const [slowPeriod, setSlowPeriod] = useState<number>(30);
  const [oversold, setOversold] = useState<number>(35);
  const [overbought, setOverbought] = useState<number>(65);

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunBacktest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const params: any = {};
      if (strategy === 'SMA' || strategy === 'EMA') {
        params.fast_period = fastPeriod;
        params.slow_period = slowPeriod;
      } else if (strategy === 'RSI') {
        params.oversold = oversold;
        params.overbought = overbought;
      }
      const data = await runBacktestSimulation({
        symbol,
        strategy,
        initial_capital: capital,
        parameters: params
      });
      setResult(data);
    } catch (err: any) {
      console.error("Backtest failed", err);
      const msg = err?.response?.data?.detail || "Historical data unavailable for this stock (minimum historical daily bars required).";
      setError(msg);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const isReturnPositive = (result?.return_percent || 0) >= 0;

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <PlayCircle className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Quantitative Strategy Backtester</h1>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Simulate algorithmic trading models against stored chronological OHLCV candles without lookahead bias.
            </p>
          </div>

          <div className="px-3 py-1.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 rounded-lg text-xs font-semibold">
            Historical Simulation Only • Zero Future Guarantee
          </div>
        </div>

        {/* Configuration Form */}
        <form onSubmit={handleRunBacktest} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mt-6 pt-5 border-t border-slate-100 dark:border-slate-800 text-xs items-end">
          <div className="lg:col-span-1">
            <SearchableStockSelector
              label="Stock Ticker"
              value={symbol}
              onChange={(sym) => setSymbol(sym)}
              placeholder="Search ticker (e.g. RELIANCE, TCS, INFY)..."
              allowClear={false}
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1">Strategy Type</label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 rounded-lg px-2.5 py-2 focus:outline-none focus:ring-1 focus:ring-emerald-500 text-xs"
            >
              <option value="SMA">SMA Golden Crossover</option>
              <option value="EMA">EMA Trend Following</option>
              <option value="RSI">RSI Mean Reversion</option>
              <option value="MACD">MACD Signal Crossover</option>
              <option value="Momentum">20-Day Momentum Breakout</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1">Starting Capital (₹)</label>
            <input
              type="number"
              value={capital}
              onChange={(e) => setCapital(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 rounded-lg px-2.5 py-2 focus:outline-none focus:ring-1 focus:ring-emerald-500 text-xs"
            />
          </div>

          {(strategy === 'SMA' || strategy === 'EMA') && (
            <>
              <div>
                <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1">Fast Period</label>
                <input
                  type="number"
                  value={fastPeriod}
                  onChange={(e) => setFastPeriod(Number(e.target.value))}
                  className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 rounded-lg px-2.5 py-2 text-xs"
                />
              </div>
              <div>
                <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1">Slow Period</label>
                <input
                  type="number"
                  value={slowPeriod}
                  onChange={(e) => setSlowPeriod(Number(e.target.value))}
                  className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 rounded-lg px-2.5 py-2 text-xs"
                />
              </div>
            </>
          )}

          {strategy === 'RSI' && (
            <>
              <div>
                <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1">Oversold Threshold</label>
                <input
                  type="number"
                  value={oversold}
                  onChange={(e) => setOversold(Number(e.target.value))}
                  className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 rounded-lg px-2.5 py-2 text-xs"
                />
              </div>
              <div>
                <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1">Overbought Threshold</label>
                <input
                  type="number"
                  value={overbought}
                  onChange={(e) => setOverbought(Number(e.target.value))}
                  className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 rounded-lg px-2.5 py-2 text-xs"
                />
              </div>
            </>
          )}

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading || !symbol}
              className="w-full px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors flex items-center justify-center gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Simulating...' : 'Execute Backtest'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Historical Data Unavailable Error Banner */}
      {error && (
        <div className="p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl text-xs text-amber-800 dark:text-amber-300 flex items-center gap-3">
          <ShieldAlert className="w-5 h-5 shrink-0 text-amber-600 dark:text-amber-400" />
          <div>
            <span className="font-bold">Historical data unavailable:</span> {error}
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Strategy Return</span>
              <div className={`text-lg font-bold mt-1 ${isReturnPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                {isReturnPositive ? '+' : ''}{result.return_percent}%
              </div>
              <span className="text-[10px] text-slate-400">Final: ₹{result.final_capital?.toLocaleString('en-IN')}</span>
            </div>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Buy & Hold Return</span>
              <div className="text-lg font-bold text-slate-800 dark:text-slate-200 mt-1">
                {result.benchmark_return >= 0 ? '+' : ''}{result.benchmark_return}%
              </div>
              <span className="text-[10px] text-slate-400">Benchmark comparison</span>
            </div>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Max Drawdown</span>
              <div className="text-lg font-bold text-rose-600 dark:text-rose-400 mt-1">
                -{result.max_drawdown}%
              </div>
              <span className="text-[10px] text-slate-400">Peak-to-trough risk</span>
            </div>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Win Rate</span>
              <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400 mt-1">
                {result.win_rate}%
              </div>
              <span className="text-[10px] text-slate-400">{result.winning_trades} / {result.completed_trades} profitable</span>
            </div>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Total Trades</span>
              <div className="text-lg font-bold text-slate-900 dark:text-white mt-1">
                {result.total_trades}
              </div>
              <span className="text-[10px] text-slate-400">Buy & sell executions</span>
            </div>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs flex flex-col justify-between">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Label</span>
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded block">
                Simulation Only
              </span>
              <span className="text-[10px] text-slate-400">Strictly non-advisory</span>
            </div>
          </div>

          {/* Trade Execution Log */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
            <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Trade Execution Log ({result.trades?.length || 0})</span>
              <span className="text-[11px] text-slate-400">{result.label}</span>
            </div>

            <div className="overflow-x-auto max-h-80 overflow-y-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-slate-100 dark:border-slate-800 sticky top-0">
                  <tr>
                    <th className="py-2.5 px-3">Date</th>
                    <th className="py-2.5 px-3">Action</th>
                    <th className="py-2.5 px-3 text-right">Price</th>
                    <th className="py-2.5 px-3 text-right">Quantity</th>
                    <th className="py-2.5 px-3 text-right">P&L</th>
                    <th className="py-2.5 px-3 text-right">P&L %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {result.trades?.map((t: any, idx: number) => {
                    const isBuy = t.type === 'BUY';
                    const hasPnl = t.pnl !== undefined;
                    const pnlPositive = (t.pnl || 0) >= 0;

                    return (
                      <tr key={idx} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40">
                        <td className="py-2 px-3 text-slate-600 dark:text-slate-400">{t.date}</td>
                        <td className="py-2 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            isBuy ? 'bg-blue-100 dark:bg-blue-950/50 text-blue-800 dark:text-blue-300' : 'bg-emerald-100 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300'
                          }`}>
                            {t.type}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-right font-semibold text-slate-900 dark:text-white">₹{t.price}</td>
                        <td className="py-2 px-3 text-right text-slate-700 dark:text-slate-300">{t.quantity}</td>
                        <td className={`py-2 px-3 text-right font-bold ${hasPnl ? (pnlPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400') : 'text-slate-400'}`}>
                          {hasPnl ? `${pnlPositive ? '+' : ''}₹${t.pnl}` : '—'}
                        </td>
                        <td className={`py-2 px-3 text-right font-bold ${hasPnl ? (pnlPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400') : 'text-slate-400'}`}>
                          {hasPnl ? `${pnlPositive ? '+' : ''}${t.pnl_percent}%` : '—'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
