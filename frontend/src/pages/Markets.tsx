import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, Activity, ArrowUpRight, ArrowDownRight, Layers } from 'lucide-react';
import { fetchMarketOverview } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';

export const Markets: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetchMarketOverview();
        setData(res);
      } catch (e) {
        console.error(e);
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

  const indices = data?.indices || [];
  const gainers = data?.top_gainers || [];
  const losers = data?.top_losers || [];
  const active = data?.most_active || [];
  const stats = data?.market_stats || {};

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-colors">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Indian Market Indices & Breadth</h1>
            <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
              {data?.market_session?.session || data?.data_status || 'Session Active'}
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Tracking Indian benchmark indices, sectoral movements, market breadth, and liquidity leaders.
          </p>
        </div>
        <StatusBadge 
          status={data?.data_status || 'Live Community'} 
          source={data?.source || 'NSE/BSE Public Feed'} 
          lastUpdated={data?.as_of_timestamp || data?.updated_at} 
        />
      </div>

      {/* Indices Grid - Compliant with Section 16 & Section 9 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {indices.length === 0 ? (
          <div className="col-span-full p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-xs rounded-lg">
            Live data unavailable. Verifying upstream market feeds.
          </div>
        ) : (
          indices.map((idx: any) => {
            const indexName = idx.index_name || idx.name;
            const price = Number(idx.value);
            const isUp = idx.change >= 0;
            const isUnavailable = !price || price <= 0;

            if (isUnavailable) {
              return (
                <div key={indexName} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs flex flex-col justify-between transition-colors">
                  <div>
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block">{indexName}</span>
                    <span className="text-xs text-rose-500 font-medium mt-2 block">Live data unavailable</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-2">Source: {idx.source || 'NSE'}</div>
                </div>
              );
            }

            return (
              <div key={indexName} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs hover:border-emerald-300 dark:hover:border-emerald-700 transition-all flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block truncate">{indexName}</span>
                    <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${
                      idx.status === 'Verified' ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}>
                      {idx.status || 'Verified'}
                    </span>
                  </div>
                  <div className="text-xl font-extrabold text-slate-900 dark:text-white mt-1.5">
                    ₹{price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>
                  <div className={`flex items-center gap-1 text-xs font-bold mt-1 ${isUp ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                    {isUp ? <ArrowUpRight className="w-4 h-4 shrink-0" /> : <ArrowDownRight className="w-4 h-4 shrink-0" />}
                    <span>{isUp ? '+' : ''}{Number(idx.change).toFixed(2)} ({isUp ? '+' : ''}{Number(idx.change_percent).toFixed(2)}%)</span>
                  </div>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-100 dark:border-slate-800 text-[10px] text-slate-400 space-y-0.5">
                  <div className="truncate"><span className="text-slate-500 dark:text-slate-400 font-medium">Source:</span> {idx.source || 'NSE Public Feed'}</div>
                  <div className="truncate"><span className="text-slate-500 dark:text-slate-400 font-medium">Updated:</span> {idx.timestamp}</div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Movers 3-column table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gainers */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs transition-colors">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-400 font-bold text-xs">
              <TrendingUp className="w-4 h-4" />
              <span>Top Gainers</span>
            </div>
            <span className="text-[10px] text-slate-400">
              Snapshot: {gainers[0]?.as_of || data?.as_of_timestamp || 'Latest'}
            </span>
          </div>
          <div className="space-y-2">
            {gainers.length === 0 ? (
              <div className="text-xs text-slate-400 py-4 text-center">No gainer data available</div>
            ) : (
              gainers.map((g: any) => (
                <div key={g.symbol} className="flex justify-between items-center p-2 rounded hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors">
                  <Link to={`/stocks/${g.symbol}`} className="font-semibold text-xs text-slate-800 dark:text-slate-200 hover:text-emerald-600 dark:hover:text-emerald-400">
                    {g.symbol}
                  </Link>
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">₹{Number(g.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                    <span className="block text-[11px] font-bold text-emerald-600 dark:text-emerald-400">+{Number(g.change_percent).toFixed(2)}%</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Losers */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs transition-colors">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-1.5 text-rose-700 dark:text-rose-400 font-bold text-xs">
              <TrendingDown className="w-4 h-4" />
              <span>Top Losers</span>
            </div>
            <span className="text-[10px] text-slate-400">
              Snapshot: {losers[0]?.as_of || data?.as_of_timestamp || 'Latest'}
            </span>
          </div>
          <div className="space-y-2">
            {losers.length === 0 ? (
              <div className="text-xs text-slate-400 py-4 text-center">No loser data available</div>
            ) : (
              losers.map((l: any) => (
                <div key={l.symbol} className="flex justify-between items-center p-2 rounded hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors">
                  <Link to={`/stocks/${l.symbol}`} className="font-semibold text-xs text-slate-800 dark:text-slate-200 hover:text-emerald-600 dark:hover:text-emerald-400">
                    {l.symbol}
                  </Link>
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">₹{Number(l.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                    <span className="block text-[11px] font-bold text-rose-600 dark:text-rose-400">{Number(l.change_percent).toFixed(2)}%</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Most Active by Volume */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs transition-colors">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300 font-bold text-xs">
              <Activity className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Most Active by Volume</span>
            </div>
            <span className="text-[10px] text-slate-400">
              Snapshot: {active[0]?.as_of || data?.as_of_timestamp || 'Latest'}
            </span>
          </div>
          <div className="space-y-2">
            {active.length === 0 ? (
              <div className="text-xs text-slate-400 py-4 text-center">No volume data available</div>
            ) : (
              active.map((a: any) => (
                <div key={a.symbol} className="flex justify-between items-center p-2 rounded hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors">
                  <Link to={`/stocks/${a.symbol}`} className="font-semibold text-xs text-slate-800 dark:text-slate-200 hover:text-emerald-600 dark:hover:text-emerald-400">
                    {a.symbol}
                  </Link>
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">₹{Number(a.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                    <span className="block text-[10px] text-slate-400 font-medium">Vol: {Number(a.volume)?.toLocaleString('en-IN')}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
