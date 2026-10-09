import React, { useEffect, useState } from 'react';
import { Layers, TrendingUp, TrendingDown, Activity, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { fetchSectors } from '../api/client';

export const Sectors: React.FC = () => {
  const [sectors, setSectors] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetchSectors();
        setSectors(res.sectors || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="w-8 h-8 border-3 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs transition-colors">
        <div className="flex items-center gap-2">
          <Layers className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
          <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Sectoral Performance & Breadth Matrix</h1>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Performance, cumulative market capitalization, and gainer/loser distribution across 12 core Indian economic sectors.
        </p>
      </div>

      {/* Grid of Sector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {sectors.map((sec) => {
          const isUp = sec.average_return >= 0;
          return (
            <div key={sec.sector} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs hover:border-emerald-300 dark:hover:border-emerald-700 transition-colors">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-sm text-slate-900 dark:text-white">{sec.sector}</h3>
                  <span className="text-[11px] text-slate-400">{sec.count} Tracked Equities</span>
                </div>
                <div className={`flex items-center gap-0.5 text-xs font-bold px-2 py-0.5 rounded ${
                  isUp 
                    ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300' 
                    : 'bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300'
                }`}>
                  {isUp ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                  <span>{isUp ? '+' : ''}{sec.average_return}%</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 block font-medium">Market Cap (Cr)</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    ₹{sec.total_market_cap_cr ? sec.total_market_cap_cr?.toLocaleString('en-IN') : '—'}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-medium">Daily Volume</span>
                  <span className="font-semibold text-slate-700 dark:text-slate-300">
                    {sec.total_volume ? sec.total_volume?.toLocaleString('en-IN') : '—'}
                  </span>
                </div>
              </div>

              {/* Breadth Bar */}
              <div className="mt-3 pt-3 border-t border-slate-50 dark:border-slate-800/60">
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-emerald-600 dark:text-emerald-400 font-semibold">{sec.gainers} Gainers</span>
                  <span className="text-rose-600 dark:text-rose-400 font-semibold">{sec.losers} Losers</span>
                </div>
                <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full flex overflow-hidden">
                  <div
                    style={{ width: `${(sec.gainers / Math.max(1, sec.gainers + sec.losers)) * 100}%` }}
                    className="bg-emerald-500"
                  />
                  <div
                    style={{ width: `${(sec.losers / Math.max(1, sec.gainers + sec.losers)) * 100}%` }}
                    className="bg-rose-500"
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
