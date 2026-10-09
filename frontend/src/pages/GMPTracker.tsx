import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, RefreshCw, AlertCircle, TrendingUp, Info, CheckCircle2 } from 'lucide-react';
import { fetchGMP, GMPItem } from '../api/client';

export const GMPTracker: React.FC = () => {
  const [gmpList, setGmpList] = useState<GMPItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [syncing, setSyncing] = useState<boolean>(false);
  const [disclaimer, setDisclaimer] = useState<string>('');
  const [attribution, setAttribution] = useState<string>('');

  const loadData = async (refresh: boolean = false) => {
    if (refresh) setSyncing(true);
    else setLoading(true);
    try {
      const res = await fetchGMP(refresh);
      setGmpList(res.data || []);
      setDisclaimer(res.disclaimer);
      setAttribution(res.attribution);
    } catch (err) {
      console.error("Failed to fetch GMP data", err);
    } finally {
      setLoading(false);
      setSyncing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs transition-colors">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-6 h-6 text-amber-600 dark:text-amber-400" />
              <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
                Unofficial Grey Market Premium (GMP) Signals
              </h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300">
                UNOFFICIAL GMP
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Independent secondary grey market indicators aggregated from community and market participant disclosures.
            </p>
          </div>

          <button
            onClick={() => loadData(true)}
            disabled={syncing}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors self-start md:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
            <span>{syncing ? 'Syncing...' : 'Sync Live GMP'}</span>
          </button>
        </div>

        {/* Mandatory Legal Warning (Section 11 Compliance) */}
        <div className="mt-5 p-3.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 rounded-xl text-xs text-amber-900 dark:text-amber-200 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">
              {disclaimer || "GMP is unofficial and unregulated. It is not an NSE/BSE price and is not a guaranteed listing indicator."}
            </p>
            <p className="text-[11px] text-amber-800 dark:text-amber-300 mt-1">
              <strong>Calculation Standard:</strong> Indicative GMP-based estimate = Upper Price Band + GMP. Do not treat GMP as official market discovery or guaranteed profit.
            </p>
          </div>
        </div>
      </div>

      {/* GMP Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs transition-colors">
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
            Tracked Grey Market Offerings ({gmpList.length})
          </span>
          <span className="text-[11px] text-slate-400 dark:text-slate-500 italic">{attribution}</span>
        </div>

        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="w-6 h-6 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : gmpList.length === 0 ? (
          <div className="p-12 text-center text-slate-500 dark:text-slate-400 text-xs">
            No live unofficial GMP quotes available currently.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-slate-100 dark:border-slate-800">
                <tr>
                  <th className="py-3 px-4">Company Name</th>
                  <th className="py-3 px-4 text-right">Unofficial GMP</th>
                  <th className="py-3 px-4 text-right">GMP %</th>
                  <th className="py-3 px-4 text-right">Reported Range</th>
                  <th className="py-3 px-4 text-right">Indicative GMP-based estimate</th>
                  <th className="py-3 px-4 text-right">Indicative Est. Gain</th>
                  <th className="py-3 px-4">Last Updated</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {gmpList.map((item) => {
                  const isPositive = item.gmp >= 0;
                  return (
                    <tr key={item.id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 font-semibold text-slate-900 dark:text-white">
                        {item.ipo_id ? (
                          <Link to={`/ipos/${item.ipo_id}`} className="hover:text-emerald-600 dark:hover:text-emerald-400 underline-offset-2 hover:underline">
                            {item.company_name}
                          </Link>
                        ) : (
                          item.company_name
                        )}
                      </td>
                      <td className={`py-3 px-4 text-right font-bold ${isPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                        ₹{item.gmp}
                      </td>
                      <td className={`py-3 px-4 text-right font-bold ${isPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                        {item.gmp_percent !== null && item.gmp_percent !== undefined ? `${item.gmp_percent >= 0 ? '+' : ''}${item.gmp_percent}%` : '—'}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-600 dark:text-slate-400">
                        {item.min_gmp && item.max_gmp ? `₹${item.min_gmp} – ₹${item.max_gmp}` : '—'}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-slate-900 dark:text-white">
                        {item.estimated_listing_price ? `₹${item.estimated_listing_price}` : 'Not Available'}
                      </td>
                      <td className={`py-3 px-4 text-right font-bold ${isPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                        {item.estimated_listing_gain !== null && item.estimated_listing_gain !== undefined ? `${item.estimated_listing_gain >= 0 ? '+' : ''}${item.estimated_listing_gain}%` : 'Not Available'}
                      </td>
                      <td className="py-3 px-4 text-slate-400 dark:text-slate-500 text-[11px]">
                        {item.timestamp}
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
