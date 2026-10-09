import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, Trash2, ArrowUpRight, ArrowDownRight, Plus, Sparkles } from 'lucide-react';
import { fetchWatchlist, addToWatchlist, removeFromWatchlist } from '../api/client';
import { SearchableStockSelector } from '../components/SearchableStockSelector';

export const Watchlist: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [newSymbol, setNewSymbol] = useState<string>('RELIANCE');

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchWatchlist();
      setItems(res.watchlist || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol) return;
    try {
      await addToWatchlist(newSymbol.toUpperCase());
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleRemove = async (id: number) => {
    try {
      await removeFromWatchlist(id);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Bookmark className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Personal Stock Watchlist</h1>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Track key equities with real-time cached price markers and embedded walk-forward ML directional forecasts.
          </p>
        </div>

        {/* Add Stock Quick Form */}
        <form onSubmit={handleAdd} className="flex items-center gap-2 w-full sm:w-auto">
          <div className="w-64">
            <SearchableStockSelector
              value={newSymbol}
              onChange={(sym) => setNewSymbol(sym)}
              placeholder="Search ticker to add..."
              allowClear={false}
            />
          </div>
          <button
            type="submit"
            disabled={!newSymbol}
            className="flex items-center gap-1 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors shrink-0"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add</span>
          </button>
        </form>
      </div>

      {/* Watchlist Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="w-6 h-6 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500 dark:text-slate-400">
            Your watchlist is currently empty. Select a ticker above to track it!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-slate-100 dark:border-slate-800">
                <tr>
                  <th className="py-3 px-4">Symbol</th>
                  <th className="py-3 px-4 text-right">Current Price</th>
                  <th className="py-3 px-4 text-right">Change</th>
                  <th className="py-3 px-4 text-right">P/E Ratio</th>
                  <th className="py-3 px-4 text-right">52W Range</th>
                  <th className="py-3 px-4">AI Forecast Snippet</th>
                  <th className="py-3 px-4 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {items.map((item) => {
                  const isUp = item.change >= 0;
                  const pred = item.prediction;

                  return (
                    <tr key={item.id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40">
                      <td className="py-3 px-4">
                        <Link to={`/stocks/${item.symbol}`} className="font-bold text-slate-900 dark:text-white hover:text-emerald-600 dark:hover:text-emerald-400 text-sm block">
                          {item.symbol}
                        </Link>
                        <span className="text-[11px] text-slate-400 font-normal">{item.name}</span>
                      </td>
                      <td className="py-3 px-4 text-right font-extrabold text-slate-900 dark:text-white text-sm">
                        {item.current_price && item.current_price > 0 ? (
                          `₹${item.current_price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                        ) : (
                          <span className="text-slate-400 font-normal text-xs">Awaiting Quote</span>
                        )}
                      </td>
                      <td className={`py-3 px-4 text-right font-bold ${isUp ? 'text-emerald-600 dark:text-emerald-400' : (item.change ?? 0) < 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-400 font-normal'}`}>
                        {item.change !== null && item.change !== undefined && item.current_price ? (
                          `${isUp ? '+' : ''}${Number(item.change).toFixed(2)} (${isUp ? '+' : ''}${Number(item.change_percent ?? 0).toFixed(2)}%)`
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-700 dark:text-slate-300 font-medium">
                        {item.pe_ratio && item.pe_ratio > 0 ? `${Number(item.pe_ratio).toFixed(1)}x` : '—'}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-600 dark:text-slate-400 text-[11px] whitespace-nowrap">
                        {item.low_52w && item.high_52w && item.low_52w > 0 && item.high_52w > 0 ? (
                          `₹${Number(item.low_52w).toLocaleString('en-IN')} – ₹${Number(item.high_52w).toLocaleString('en-IN')}`
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="py-3 px-4">
                        {pred ? (
                          <div className="flex items-center gap-1.5 text-[11px]">
                            <Sparkles className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                            <span className="font-semibold text-slate-800 dark:text-slate-200">{pred.positive_prob}% Upside</span>
                            <span className="text-slate-400">({pred.range})</span>
                          </div>
                        ) : (
                          <span className="text-slate-400 text-[11px]">Pending candles</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <button
                          onClick={() => handleRemove(item.id)}
                          className="p-1 rounded text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
                          title="Remove from watchlist"
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
    </div>
  );
};
