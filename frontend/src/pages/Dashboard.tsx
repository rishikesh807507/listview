import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, 
  Sparkles, PieChart, ShieldCheck, Activity, BarChart3, ChevronRight 
} from 'lucide-react';
import { fetchMarketOverview, fetchIPOs, fetchBatchPredictions } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';

export const Dashboard: React.FC = () => {
  const [marketData, setMarketData] = useState<any>(null);
  const [ipos, setIpos] = useState<any[]>([]);
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [mkt, ipoList, preds] = await Promise.all([
          fetchMarketOverview(),
          fetchIPOs({ limit: 4 }),
          fetchBatchPredictions()
        ]);
        setMarketData(mkt);
        setIpos(ipoList.slice(0, 4));
        setPredictions(preds.predictions ? preds.predictions.slice(0, 4) : []);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-3 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-xs text-slate-500 font-medium">Loading market intelligence...</span>
        </div>
      </div>
    );
  }

  const indices = marketData?.indices || [];
  const gainers = marketData?.top_gainers || [];
  const losers = marketData?.top_losers || [];
  const stats = marketData?.market_stats || { advances: 0, declines: 0, unchanged: 0 };

  return (
    <div className="space-y-6">
      {/* Top Banner with Data Status */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Listview — Indian Stocks & IPO Intelligence</h1>
            <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
              {marketData?.market_session?.session || marketData?.data_status || 'Session Active'}
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Factual exchange disclosures, local database caching, walk-forward AI directional forecasting, and unofficial GMP tracking.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge
            status={marketData?.data_status || "Live Community"}
            source={marketData?.source || "NSE/BSE Public Feed"}
            lastUpdated={marketData?.as_of_timestamp || marketData?.updated_at}
          />
          <Link
            to="/settings/data-health"
            className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span>Data Health</span>
          </Link>
          <Link
            to="/screener"
            className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
          >
            Launch Screener
          </Link>
        </div>
      </div>

      {/* Benchmark Indices Ticker Cards - Compliant with Section 16 & Section 9 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        {indices.length === 0 ? (
          <div className="col-span-full p-4 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 text-amber-800 dark:text-amber-300 text-xs rounded-lg">
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
                <div key={indexName} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3.5 shadow-xs flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block">{indexName}</span>
                    <span className="text-xs text-rose-500 font-medium mt-2 block">Live data unavailable</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-2">Source: {idx.source || 'NSE'}</div>
                </div>
              );
            }

            return (
              <div key={indexName} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3.5 shadow-xs hover:border-emerald-300 dark:hover:border-emerald-600 transition-all flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block truncate">{indexName}</span>
                    <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${
                      idx.status === 'Verified' ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}>
                      {idx.status || 'Verified'}
                    </span>
                  </div>
                  
                  <div className="text-base font-extrabold text-slate-900 dark:text-white mt-1">
                    ₹{price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>

                  <div className={`flex items-center gap-1 text-xs font-bold mt-1 ${isUp ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                    {isUp ? <ArrowUpRight className="w-3.5 h-3.5 shrink-0" /> : <ArrowDownRight className="w-3.5 h-3.5 shrink-0" />}
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

      {/* Middle Grid: Market Movers & Advances/Declines */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Gainers */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-400 font-semibold text-xs">
                <TrendingUp className="w-4 h-4" />
                <span>Top Gainers (NSE)</span>
              </div>
              <span className="text-[10px] text-slate-400 block mt-0.5">
                Snapshot: {gainers[0]?.as_of || marketData?.as_of_timestamp || 'Latest'}
              </span>
            </div>
            <Link to="/markets" className="text-[11px] text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 flex items-center">
              More <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="space-y-2.5">
            {gainers.length === 0 ? (
              <div className="text-xs text-slate-400 py-4 text-center">No gainer data available</div>
            ) : (
              gainers.map((g: any) => (
                <Link
                  key={g.symbol}
                  to={`/stocks/${g.symbol}`}
                  className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors"
                >
                  <div>
                    <span className="font-semibold text-xs text-slate-800 dark:text-slate-200">{g.symbol}</span>
                    <span className="block text-[11px] text-slate-400 truncate max-w-[120px]">{g.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold text-slate-900 dark:text-white">₹{Number(g.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                    <span className="block text-[11px] font-bold text-emerald-600 dark:text-emerald-400">+{Number(g.change_percent).toFixed(2)}%</span>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        {/* Top Losers */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <div className="flex items-center gap-1.5 text-rose-700 dark:text-rose-400 font-semibold text-xs">
                <TrendingDown className="w-4 h-4" />
                <span>Top Losers (NSE)</span>
              </div>
              <span className="text-[10px] text-slate-400 block mt-0.5">
                Snapshot: {losers[0]?.as_of || marketData?.as_of_timestamp || 'Latest'}
              </span>
            </div>
            <Link to="/markets" className="text-[11px] text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 flex items-center">
              More <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="space-y-2.5">
            {losers.length === 0 ? (
              <div className="text-xs text-slate-400 py-4 text-center">No loser data available</div>
            ) : (
              losers.map((l: any) => (
                <Link
                  key={l.symbol}
                  to={`/stocks/${l.symbol}`}
                  className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors"
                >
                  <div>
                    <span className="font-semibold text-xs text-slate-800 dark:text-slate-200">{l.symbol}</span>
                    <span className="block text-[11px] text-slate-400 truncate max-w-[120px]">{l.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold text-slate-900 dark:text-white">₹{Number(l.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                    <span className="block text-[11px] font-bold text-rose-600 dark:text-rose-400">{Number(l.change_percent).toFixed(2)}%</span>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        {/* Market Breadth & Statistics */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-1.5 text-slate-800 dark:text-slate-200 font-semibold text-xs">
                <Activity className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <span>Market Breadth & Statistics</span>
              </div>
              <span className="text-[11px] text-slate-400">NSE Active</span>
            </div>

            {/* Advance/Decline visual bar */}
            <div className="space-y-1.5 mt-2">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-emerald-600 dark:text-emerald-400 font-semibold">{stats.advances} Advances</span>
                <span className="text-slate-400">{stats.unchanged} Flat</span>
                <span className="text-rose-600 dark:text-rose-400 font-semibold">{stats.declines} Declines</span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full flex overflow-hidden">
                <div style={{ width: `${(stats.advances / Math.max(1, stats.advances + stats.declines + stats.unchanged)) * 100}%` }} className="bg-emerald-500" />
                <div style={{ width: `${(stats.unchanged / Math.max(1, stats.advances + stats.declines + stats.unchanged)) * 100}%` }} className="bg-slate-300 dark:bg-slate-600" />
                <div style={{ width: `${(stats.declines / Math.max(1, stats.advances + stats.declines + stats.unchanged)) * 100}%` }} className="bg-rose-500" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-lg">
                <span className="text-[10px] text-slate-400 block uppercase font-bold tracking-wider">A/D Ratio</span>
                <span className="text-sm font-bold text-slate-800 dark:text-slate-200">{stats.advance_decline_ratio || '1.0'}</span>
              </div>
              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-lg">
                <span className="text-[10px] text-slate-400 block uppercase font-bold tracking-wider">52W Highs/Lows</span>
                <span className="text-sm font-bold text-slate-800 dark:text-slate-200">{stats.highs_52w} / {stats.lows_52w}</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
            <span className="text-[11px] text-slate-400 block">
              Market data synced locally into SQLite database. Graceful offline fallback active.
            </span>
          </div>
        </div>
      </div>

      {/* Featured Sections: IPO Intelligence & Walk-Forward AI Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* IPO Center Preview */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <PieChart className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">IPO Radar & Grey Market Premium</h3>
                <span className="text-[10px] text-slate-400">Open-source GMP dataset + Official issue details</span>
              </div>
            </div>
            <Link to="/ipos" className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 flex items-center">
              All IPOs <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {ipos.map((ipo) => (
              <div key={ipo.id} className="p-3 rounded-lg border border-slate-100 dark:border-slate-800 hover:border-slate-200 dark:hover:border-slate-700 transition-colors">
                <div className="flex items-start justify-between">
                  <div>
                    <Link to={`/ipos/${ipo.id}`} className="font-semibold text-xs text-slate-900 dark:text-white hover:text-emerald-600 dark:hover:text-emerald-400">
                      {ipo.company_name}
                    </Link>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                        {ipo.ipo_type}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                        ipo.status === 'Open' ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300' : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
                      }`}>
                        {ipo.status}
                      </span>
                      <span className="text-[11px] text-slate-400">₹{ipo.issue_size} Cr</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-[11px] text-slate-400 block">Unofficial GMP</span>
                    <span className={`text-xs font-bold ${Number(ipo.gmp) >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                      {ipo.gmp ? `₹${ipo.gmp} (${ipo.gmp_percent}%)` : 'N/A'}
                    </span>
                    {ipo.estimated_listing_price && (
                      <span className="block text-[10px] text-slate-500 dark:text-slate-400">
                        Est: ₹{ipo.estimated_listing_price}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-3 text-[10px] text-amber-700 dark:text-amber-400 bg-amber-50/60 dark:bg-amber-950/30 p-2 rounded border border-amber-200/50 dark:border-amber-900/40">
            GMP is unofficial and unregulated. It is not an NSE/BSE price and not a guaranteed listing price.
          </div>
        </div>

        {/* AI Predictions Preview */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">AI Directional Forecasts</h3>
                <span className="text-[10px] text-slate-400">TimeSeriesSplit walk-forward validation (Strict no-lookahead)</span>
              </div>
            </div>
            <Link to="/predictions" className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 flex items-center">
              All Forecasts <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {predictions.map((p) => (
              <div key={p.symbol} className="p-3 rounded-lg border border-slate-100 dark:border-slate-800 hover:border-slate-200 dark:hover:border-slate-700 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <Link to={`/stocks/${p.symbol}`} className="font-semibold text-xs text-slate-900 dark:text-white hover:text-emerald-600 dark:hover:text-emerald-400">
                      {p.symbol}
                    </Link>
                    <span className="block text-[11px] text-slate-400">
                      {p.name}{p.current_price && p.current_price > 0 ? ` • ₹${Number(p.current_price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : ''}
                    </span>
                  </div>

                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">
                      {p.positive_prob}% Upside Prob
                    </span>
                    <span className="block text-[11px] text-slate-500 dark:text-slate-400">
                      Band: {p.expected_return_range}
                    </span>
                  </div>
                </div>

                <div className="mt-2 pt-2 border-t border-slate-50 dark:border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                  <span>Model: {p.model_name}</span>
                  <span>Accuracy: {p.walk_forward_accuracy}</span>
                  <span className={`px-1.5 py-0.5 rounded font-medium ${
                    p.confidence === 'High' ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300' : 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300'
                  }`}>
                    {p.confidence} Conf.
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-3 text-[10px] text-slate-400 bg-slate-50 dark:bg-slate-800/60 p-2 rounded border border-slate-100 dark:border-slate-800">
            Open-source ML models (Random Forest/XGBoost). Never treated as guaranteed return or financial advice.
          </div>
        </div>
      </div>
    </div>
  );
};
