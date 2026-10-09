import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Filter, Search, RotateCcw, Check, Bookmark, ArrowUpDown } from 'lucide-react';
import { fetchScreenerResults, fetchSavedScreens } from '../api/client';

export const Screener: React.FC = () => {
  const [results, setResults] = useState<any[]>([]);
  const [savedScreens, setSavedScreens] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Filter States
  const [minRoe, setMinRoe] = useState<string>('');
  const [maxDebtToEquity, setMaxDebtToEquity] = useState<string>('');
  const [minRevGrowth, setMinRevGrowth] = useState<string>('');
  const [maxPe, setMaxPe] = useState<string>('');
  const [minDivYield, setMinDivYield] = useState<string>('');
  const [selectedSector, setSelectedSector] = useState<string>('all');

  const executeScreen = async (overrideParams?: any) => {
    setLoading(true);
    try {
      const params: any = overrideParams || {};
      if (!overrideParams) {
        if (minRoe) params.min_roe = Number(minRoe);
        if (maxDebtToEquity) params.max_debt_to_equity = Number(maxDebtToEquity);
        if (minRevGrowth) params.min_rev_growth = Number(minRevGrowth);
        if (maxPe) params.max_pe = Number(maxPe);
        if (minDivYield) params.min_dividend_yield = Number(minDivYield);
        if (selectedSector !== 'all') params.sector = selectedSector;
      }
      const res = await fetchScreenerResults(params);
      setResults(res.results || []);
    } catch (err) {
      console.error("Error executing screen", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        const screens = await fetchSavedScreens();
        setSavedScreens(screens || []);
      } catch (e) {
        console.error(e);
      }
      executeScreen();
    };
    init();
  }, []);

  const applyPreset = (preset: any) => {
    const f = preset.filters;
    setMinRoe(f.min_roe ? String(f.min_roe) : '');
    setMaxDebtToEquity(f.max_debt_to_equity ? String(f.max_debt_to_equity) : '');
    setMinRevGrowth(f.min_rev_growth ? String(f.min_rev_growth) : '');
    setMaxPe(f.max_pe ? String(f.max_pe) : '');
    setMinDivYield(f.min_dividend_yield ? String(f.min_dividend_yield) : '');
    executeScreen(f);
  };

  const resetFilters = () => {
    setMinRoe('');
    setMaxDebtToEquity('');
    setMinRevGrowth('');
    setMaxPe('');
    setMinDivYield('');
    setSelectedSector('all');
    executeScreen({});
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs transition-colors">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Filter className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Fundamental Stock Screener</h1>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Filter by valuation, capital efficiency, leverage, and growth metrics across local database records.
            </p>
          </div>

          {/* Preset Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-slate-400 mr-1">Presets:</span>
            {savedScreens.map((s) => (
              <button
                key={s.id}
                onClick={() => applyPreset(s)}
                className="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 hover:text-emerald-700 dark:hover:text-emerald-300 text-slate-700 dark:text-slate-300 transition-colors"
                title={s.description}
              >
                {s.name}
              </button>
            ))}
          </div>
        </div>

        {/* Filters Input Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-6 pt-5 border-t border-slate-100 dark:border-slate-800 text-xs">
          <div>
            <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 block mb-1">Min ROE (%)</label>
            <input
              type="number"
              placeholder="e.g. 15"
              value={minRoe}
              onChange={(e) => setMinRoe(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 block mb-1">Max Debt/Equity</label>
            <input
              type="number"
              step="0.1"
              placeholder="e.g. 0.5"
              value={maxDebtToEquity}
              onChange={(e) => setMaxDebtToEquity(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 block mb-1">Min Rev Growth (%)</label>
            <input
              type="number"
              placeholder="e.g. 10"
              value={minRevGrowth}
              onChange={(e) => setMinRevGrowth(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 block mb-1">Max P/E</label>
            <input
              type="number"
              placeholder="e.g. 30"
              value={maxPe}
              onChange={(e) => setMaxPe(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 block mb-1">Min Div Yield (%)</label>
            <input
              type="number"
              step="0.1"
              placeholder="e.g. 1.0"
              value={minDivYield}
              onChange={(e) => setMinDivYield(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 block mb-1">Sector</label>
            <select
              value={selectedSector}
              onChange={(e) => setSelectedSector(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            >
              <option value="all">All Sectors</option>
              <option value="IT">IT</option>
              <option value="Banking">Banking</option>
              <option value="Automobile">Automobile</option>
              <option value="Pharma">Pharma</option>
              <option value="Energy">Energy</option>
              <option value="FMCG">FMCG</option>
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-2 mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={resetFilters}
            className="flex items-center gap-1 px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
          <button
            onClick={() => executeScreen()}
            className="flex items-center gap-1 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
          >
            <span>Run Screen</span>
          </button>
        </div>
      </div>

      {/* Results Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs transition-colors">
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Screening Results ({results.length} Stocks Matched)</span>
        </div>

        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="w-6 h-6 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-slate-100 dark:border-slate-800">
                <tr>
                  <th className="py-3 px-4">Symbol</th>
                  <th className="py-3 px-4">Sector</th>
                  <th className="py-3 px-4 text-right">Price (₹)</th>
                  <th className="py-3 px-4 text-right">P/E</th>
                  <th className="py-3 px-4 text-right">ROE (%)</th>
                  <th className="py-3 px-4 text-right">ROCE (%)</th>
                  <th className="py-3 px-4 text-right">D/E</th>
                  <th className="py-3 px-4 text-right">Rev Growth</th>
                  <th className="py-3 px-4 text-right">Div Yield</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {results.map((r) => (
                  <tr key={r.symbol} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-bold text-slate-900 dark:text-white">
                      <Link to={`/stocks/${r.symbol}`} className="hover:text-emerald-600 dark:hover:text-emerald-400">
                        {r.symbol}
                      </Link>
                      <span className="block text-[11px] text-slate-400 font-normal truncate max-w-[120px]">{r.name}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-600 dark:text-slate-400">{r.sector}</td>
                    <td className="py-3 px-4 text-right font-semibold text-slate-900 dark:text-white">
                      {r.current_price && r.current_price > 0 ? `₹${Number(r.current_price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '—'}
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-slate-800 dark:text-slate-200">
                      {r.pe_ratio && r.pe_ratio > 0 ? `${Number(r.pe_ratio).toFixed(1)}x` : '—'}
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-emerald-600 dark:text-emerald-400">
                      {r.roe && r.roe !== 0 ? `${Number(r.roe).toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-slate-800 dark:text-slate-200">
                      {r.roce && r.roce !== 0 ? `${Number(r.roce).toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-slate-800 dark:text-slate-200">
                      {r.debt_to_equity !== undefined && r.debt_to_equity !== null ? `${Number(r.debt_to_equity).toFixed(2)}x` : '—'}
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-slate-800 dark:text-slate-200">
                      {r.revenue_growth ? `${r.revenue_growth > 0 ? '+' : ''}${Number(r.revenue_growth).toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-slate-800 dark:text-slate-200">
                      {r.dividend_yield ? `${Number(r.dividend_yield).toFixed(2)}%` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
