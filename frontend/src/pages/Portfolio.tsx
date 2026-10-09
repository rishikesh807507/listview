import React, { useEffect, useState } from 'react';
import { 
  Briefcase, Plus, Trash2, ArrowUpRight, ArrowDownRight, 
  PieChart as PieIcon, ShieldAlert, Check 
} from 'lucide-react';
import { fetchPortfolio, buyStock, sellStock } from '../api/client';
import { SearchableStockSelector, StockOption } from '../components/SearchableStockSelector';

export const Portfolio: React.FC = () => {
  const [portfolioData, setPortfolioData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showBuyModal, setShowBuyModal] = useState<boolean>(false);
  const [buySymbol, setBuySymbol] = useState<string>('RELIANCE');
  const [buyQty, setBuyQty] = useState<string>('10');
  const [buyPrice, setBuyPrice] = useState<string>('2980');
  const [buyNotes, setBuyNotes] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchPortfolio();
      setPortfolioData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStockSelect = (sym: string, stock?: StockOption) => {
    setBuySymbol(sym);
    if (stock && stock.current_price) {
      setBuyPrice(stock.current_price.toString());
    }
  };

  const handleBuy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!buySymbol) return;
    try {
      await buyStock({
        symbol: buySymbol.toUpperCase(),
        quantity: parseInt(buyQty),
        buy_price: parseFloat(buyPrice),
        notes: buyNotes
      });
      setShowBuyModal(false);
      loadData();
    } catch (err) {
      console.error("Buy order failed", err);
    }
  };

  const handleSell = async (itemId: number, qty: number) => {
    try {
      await sellStock(itemId, qty);
      loadData();
    } catch (err) {
      console.error("Sell order failed", err);
    }
  };

  const summary = portfolioData?.summary || { total_invested: 0, total_current_value: 0, total_pnl: 0, total_pnl_percent: 0 };
  const holdings = portfolioData?.holdings || [];
  const sectorAlloc = portfolioData?.sector_allocation || [];
  const isPnlPositive = summary.total_pnl >= 0;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Briefcase className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Virtual Portfolio Simulator</h1>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Paper trading sandbox to simulate portfolio strategies without capital risk.
          </p>
        </div>

        <button
          onClick={() => setShowBuyModal(true)}
          className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Add Position</span>
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
          <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Invested Capital</span>
          <div className="text-xl font-extrabold text-slate-900 dark:text-white mt-1">
            ₹{summary.total_invested?.toLocaleString('en-IN')}
          </div>
          <span className="text-[11px] text-slate-500 dark:text-slate-400">{summary.total_holdings_count} active positions</span>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
          <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Current Valuation</span>
          <div className="text-xl font-extrabold text-slate-900 dark:text-white mt-1">
            ₹{summary.total_current_value?.toLocaleString('en-IN')}
          </div>
          <span className="text-[11px] text-slate-500 dark:text-slate-400">Live database marks</span>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
          <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Total Profit / Loss</span>
          <div className={`text-xl font-extrabold mt-1 flex items-center gap-1 ${isPnlPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
            {isPnlPositive ? <ArrowUpRight className="w-5 h-5" /> : <ArrowDownRight className="w-5 h-5" />}
            <span>₹{summary.total_pnl?.toLocaleString('en-IN')}</span>
          </div>
          <span className={`text-[11px] font-bold ${isPnlPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
            {isPnlPositive ? '+' : ''}{summary.total_pnl_percent}% overall return
          </span>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Simulated Account</span>
          <div className="text-sm font-semibold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-1 rounded w-fit mt-1">
            Virtual Paper Account
          </div>
          <span className="text-[10px] text-slate-400 mt-1">Zero real money or execution risk</span>
        </div>
      </div>

      {/* Holdings & Sector Allocation Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Holdings Table */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
          <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Portfolio Holdings ({holdings.length})</span>
          </div>

          {holdings.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500 dark:text-slate-400">
              No holdings yet. Click "Add Position" to record your first simulated trade!
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-slate-100 dark:border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3">Asset</th>
                    <th className="py-2.5 px-3 text-right">Qty</th>
                    <th className="py-2.5 px-3 text-right">Avg Price</th>
                    <th className="py-2.5 px-3 text-right">Cur. Price</th>
                    <th className="py-2.5 px-3 text-right">Cur. Value</th>
                    <th className="py-2.5 px-3 text-right">P&L</th>
                    <th className="py-2.5 px-3 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {holdings.map((h: any) => {
                    const up = h.profit_loss >= 0;
                    return (
                      <tr key={h.id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40">
                        <td className="py-2.5 px-3">
                          <span className="font-bold text-slate-900 dark:text-white block">{h.symbol}</span>
                          <span className="text-[10px] text-slate-400">{h.sector}</span>
                        </td>
                        <td className="py-2.5 px-3 text-right font-medium text-slate-800 dark:text-slate-200">{h.quantity}</td>
                        <td className="py-2.5 px-3 text-right text-slate-600 dark:text-slate-400">₹{Number(h.buy_price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                        <td className="py-2.5 px-3 text-right font-semibold text-slate-900 dark:text-white">
                          {h.current_price && h.current_price > 0 ? `₹${Number(h.current_price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '—'}
                        </td>
                        <td className="py-2.5 px-3 text-right font-bold text-slate-900 dark:text-white">
                          ₹{Number(h.current_value ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </td>
                        <td className={`py-2.5 px-3 text-right font-bold ${up ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                          {up ? '+' : ''}₹{Number(h.profit_loss ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })} ({up ? '+' : ''}{Number(h.return_percent ?? 0).toFixed(2)}%)
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          <button
                            onClick={() => handleSell(h.id, h.quantity)}
                            className="p-1 rounded text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
                            title="Sell entire position"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Sector Allocation Breakdown */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 pb-3 mb-3 border-b border-slate-100 dark:border-slate-800">
              <PieIcon className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">Sector Allocation</h3>
            </div>

            <div className="space-y-3">
              {sectorAlloc.map((sec: any) => (
                <div key={sec.sector} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-medium text-slate-700 dark:text-slate-300">{sec.sector}</span>
                    <span className="font-bold text-slate-900 dark:text-white">{sec.percent}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div style={{ width: `${sec.percent}%` }} className="h-full bg-emerald-500 rounded-full" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400">
            {portfolioData?.disclaimer}
          </div>
        </div>
      </div>

      {/* Buy Modal */}
      {showBuyModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl max-w-sm w-full p-5 border border-slate-200 dark:border-slate-800 space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">Add Simulated Position</h3>
            <form onSubmit={handleBuy} className="space-y-3 text-xs">
              <div>
                <SearchableStockSelector
                  label="Stock Ticker"
                  value={buySymbol}
                  onChange={handleStockSelect}
                  placeholder="Search stock..."
                  allowClear={false}
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Quantity</label>
                <input
                  type="number"
                  min="1"
                  value={buyQty}
                  onChange={(e) => setBuyQty(e.target.value)}
                  className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white rounded-lg"
                  required
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Buy Price (₹)</label>
                <input
                  type="number"
                  step="0.05"
                  value={buyPrice}
                  onChange={(e) => setBuyPrice(e.target.value)}
                  className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white rounded-lg"
                  required
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowBuyModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!buySymbol}
                  className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold rounded-lg"
                >
                  Confirm Buy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
