import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Layers, Search, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';
import { fetchStocks, StockItem } from '../api/client';

export const Stocks: React.FC = () => {
  const [stocks, setStocks] = useState<StockItem[]>([]);
  const [sectorFilter, setSectorFilter] = useState<string>('all');
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await fetchStocks({
          sector: sectorFilter !== 'all' ? sectorFilter : undefined,
          search: search || undefined
        });
        setStocks(res || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [sectorFilter, search]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Layers className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Indian Equity Stocks Catalog</h1>
              <span className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded-full">
                {stocks.length} Available
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Active NSE & BSE tracked companies with stored historical records and real-time community fallback feeds.
            </p>
          </div>

          {/* Search & Sector */}
          <div className="flex items-center gap-3">
            <select
              value={sectorFilter}
              onChange={(e) => setSectorFilter(e.target.value)}
              className="text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500 font-medium"
            >
              <option value="all">All Sectors</option>
              <option value="IT">IT</option>
              <option value="Banking">Banking</option>
              <option value="Finance">Finance</option>
              <option value="Automobile">Automobile</option>
              <option value="Energy">Energy</option>
              <option value="Pharma">Pharma</option>
              <option value="FMCG">FMCG</option>
              <option value="Consumer Durables">Consumer Durables</option>
              <option value="Infrastructure">Infrastructure</option>
              <option value="Metals">Metals</option>
              <option value="Telecom">Telecom</option>
              <option value="Real Estate">Real Estate</option>
              <option value="Chemicals">Chemicals</option>
            </select>

            <div className="relative w-48 sm:w-60">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search symbol or name..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full text-xs pl-8 pr-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Stocks Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="w-6 h-6 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : stocks.length === 0 ? (
          <div className="text-center py-12 text-slate-500 dark:text-slate-400 text-xs">
            No stocks found matching the selected filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-slate-100 dark:border-slate-800">
                <tr>
                  <th className="py-3 px-4">Company</th>
                  <th className="py-3 px-4 text-right">Price (₹)</th>
                  <th className="py-3 px-4 text-right">Change</th>
                  <th className="py-3 px-4 text-right">Mkt Cap (Cr)</th>
                  <th className="py-3 px-4 text-right">P/E</th>
                  <th className="py-3 px-4 text-right">ROE</th>
                  <th className="py-3 px-4 text-right">ROCE</th>
                  <th className="py-3 px-4 text-right">52W Range</th>
                  <th className="py-3 px-4 text-center">Chart</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {stocks.map((s) => {
                  const hasPrice = s.current_price !== null && s.current_price !== undefined && s.current_price > 0;
                  const changeVal = s.change;
                  const pctVal = s.change_percent;
                  const hasChange = hasPrice && changeVal !== null && changeVal !== undefined;
                  const isUp = hasChange && changeVal > 0;
                  const isDown = hasChange && changeVal < 0;

                  return (
                    <tr key={s.symbol} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4">
                        <Link to={`/stocks/${s.symbol}`} className="font-bold text-slate-900 dark:text-white hover:text-emerald-600 dark:hover:text-emerald-400 text-sm block">
                          {s.symbol}
                        </Link>
                        <span className="text-[11px] text-slate-400 font-normal">{s.name} • {s.sector || 'Mainboard'}</span>
                      </td>
                      <td className="py-3 px-4 text-right font-extrabold text-slate-900 dark:text-white text-sm">
                        {hasPrice ? (
                          `₹${Number(s.current_price).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                        ) : (
                          <span className="text-slate-400 dark:text-slate-500 font-medium text-xs" title="Awaiting market session quote">
                            Awaiting Quote
                          </span>
                        )}
                      </td>
                      <td className={`py-3 px-4 text-right font-bold ${isUp ? 'text-emerald-600 dark:text-emerald-400' : isDown ? 'text-rose-600 dark:text-rose-400' : 'text-slate-400 dark:text-slate-500 font-normal'}`}>
                        {hasChange ? (
                          `${isUp ? '+' : ''}${Number(changeVal).toFixed(2)} (${(pctVal ?? 0) > 0 ? '+' : ''}${Number(pctVal ?? 0).toFixed(2)}%)`
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-700 dark:text-slate-300 font-semibold">
                        {s.market_cap && s.market_cap > 0 ? `₹${Number(s.market_cap).toLocaleString('en-IN')} Cr` : '—'}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-800 dark:text-slate-200 font-medium">
                        {s.pe_ratio && s.pe_ratio > 0 ? `${Number(s.pe_ratio).toFixed(1)}x` : '—'}
                      </td>
                      <td className="py-3 px-4 text-right text-emerald-600 dark:text-emerald-400 font-bold">
                        {s.roe && s.roe !== 0 ? `${Number(s.roe).toFixed(1)}%` : '—'}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-800 dark:text-slate-200 font-semibold">
                        {s.roce && s.roce !== 0 ? `${Number(s.roce).toFixed(1)}%` : '—'}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-600 dark:text-slate-400 text-[11px] whitespace-nowrap">
                        {s.low_52w && s.high_52w && s.low_52w > 0 && s.high_52w > 0 ? (
                          `₹${Number(s.low_52w).toLocaleString('en-IN')} – ₹${Number(s.high_52w).toLocaleString('en-IN')}`
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Link
                          to={`/stocks/${s.symbol}`}
                          className="px-2.5 py-1 bg-emerald-50 dark:bg-emerald-950/40 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300 rounded text-xs font-semibold inline-flex items-center gap-1 transition-colors"
                        >
                          <span>Analyze</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
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
