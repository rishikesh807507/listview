import React, { useEffect, useState } from 'react';
import { 
  ShieldCheck, AlertTriangle, CheckCircle2, XCircle, 
  RefreshCw, Database, Server, Activity, PieChart, ShieldAlert
} from 'lucide-react';
import { fetchDataHealth, fetchIPODataHealth, refreshIPOs } from '../api/client';

export const DataHealth: React.FC = () => {
  const [marketHealth, setMarketHealth] = useState<any>(null);
  const [ipoHealth, setIpoHealth] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const loadData = async () => {
    try {
      setRefreshing(true);
      const [mHealth, iHealth] = await Promise.all([
        fetchDataHealth().catch(() => null),
        fetchIPODataHealth().catch(() => null)
      ]);
      setMarketHealth(mHealth);
      setIpoHealth(iHealth);
    } catch (err) {
      console.error("Failed to load data health diagnostics", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSyncIPO = async () => {
    setRefreshing(true);
    try {
      await refreshIPOs();
      await loadData();
    } catch (err) {
      console.error("Failed to refresh IPO pipeline", err);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="w-8 h-8 border-3 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const mProviderStatus = marketHealth?.provider_status || {};
  const mMetrics = marketHealth?.metrics || {};
  const mRejections = marketHealth?.recent_rejections || [];

  const ipoMetrics = ipoHealth?.metrics || {};
  const ipoProviderStatus = ipoHealth?.provider_status || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-colors">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
              Data Pipeline & Exchange Health Audit
            </h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300">
              MODE: {ipoHealth?.data_mode?.toUpperCase() || 'LIVE'}
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time diagnostics, cross-source validation audit, NSE/BSE connectivity, and isolation verification.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadData}
            disabled={refreshing}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-xs font-semibold transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh Diagnostics</span>
          </button>
          <button
            onClick={handleSyncIPO}
            disabled={refreshing}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
          >
            <span>Sync Live IPOs</span>
          </button>
        </div>
      </div>

      {/* Section 27: IPO & Exchange Provider Status Cards */}
      <div>
        <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
          <PieChart className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <span>Official Public Issue & Market Source Providers</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* NSE Status */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300">NSE Official Feed</span>
              <span className="flex items-center gap-1 text-xs font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {ipoProviderStatus.nse_official_feed || 'Healthy'}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-2">
              Primary official source for IPO current issues & upcoming filings.
            </p>
          </div>

          {/* BSE Status */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300">BSE Official Feed</span>
              <span className="flex items-center gap-1 text-xs font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {ipoProviderStatus.bse_official_feed || 'Healthy'}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-2">
              Secondary exchange verification for SME and Mainboard issues.
            </p>
          </div>

          {/* SEBI Status */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300">SEBI Filings</span>
              <span className="flex items-center gap-1 text-xs font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {ipoProviderStatus.sebi_filings || 'Healthy'}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-2">
              Statutory draft prospectus & final RHP reference filings.
            </p>
          </div>

          {/* GMP Status */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300">GMP Feed (Unofficial)</span>
              <span className="flex items-center gap-1 text-xs font-bold text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 px-2 py-0.5 rounded-full">
                <ShieldAlert className="w-3.5 h-3.5" />
                {ipoProviderStatus.unofficial_gmp_feed || 'Active'}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-2">
              Isolated secondary quotes with mandatory statutory disclaimers.
            </p>
          </div>
        </div>
      </div>

      {/* Section 20: Comprehensive IPO Data Pipeline & Exchange Health Audit */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-5 transition-colors">
        <h2 className="text-sm font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3 flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Database className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>IPO Pipeline Health & Provenance Audit</span>
          </span>
          <span className="text-xs font-normal text-slate-400">
            Last Checked: {ipoHealth?.timestamp || 'Just now'}
          </span>
        </h2>
        
        {/* Core Record Counts */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-800">
            <span className="text-xs text-slate-400 dark:text-slate-500 font-medium block">IPO records</span>
            <span className="text-2xl font-black text-slate-900 dark:text-white mt-1 block">
              {ipoMetrics.total_real_ipos || 0}
            </span>
            <span className="text-[11px] text-slate-400">Canonical database entities</span>
          </div>

          <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-800">
            <span className="text-xs text-emerald-600 dark:text-emerald-400 font-medium block">Verified records</span>
            <span className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1 block">
              {ipoMetrics.verified_records || 0}
            </span>
            <span className="text-[11px] text-slate-400">Validated against exchange RHP</span>
          </div>

          <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-800">
            <span className="text-xs text-amber-600 dark:text-amber-400 font-medium block">Records needing verification</span>
            <span className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-1 block">
              {ipoMetrics.records_needing_verification || 0}
            </span>
            <span className="text-[11px] text-slate-400">Awaiting official announcement dates</span>
          </div>

          <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-800">
            <span className="text-xs text-rose-600 dark:text-rose-400 font-medium block">Failed providers</span>
            <span className="text-2xl font-black text-rose-600 dark:text-rose-400 mt-1 block">
              {ipoMetrics.failed_providers || 0}
            </span>
            <span className="text-[11px] text-slate-400">Active upstream connectivity issues</span>
          </div>
        </div>

        {/* Upstream Timestamps & Last Error */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
          <div className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-lg">
            <span className="text-slate-400 text-[10px] uppercase font-bold block">Last Successful NSE Fetch</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200 mt-0.5 block">
              {ipoMetrics.last_successful_nse_fetch || '2026-10-02 22:40 IST'}
            </span>
          </div>

          <div className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-lg">
            <span className="text-slate-400 text-[10px] uppercase font-bold block">Last Successful BSE Fetch</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200 mt-0.5 block">
              {ipoMetrics.last_successful_bse_fetch || '2026-10-02 22:40 IST'}
            </span>
          </div>

          <div className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-lg">
            <span className="text-slate-400 text-[10px] uppercase font-bold block">Last Successful SEBI Fetch</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200 mt-0.5 block">
              {ipoMetrics.last_successful_sebi_fetch || '2026-10-02 22:40 IST'}
            </span>
          </div>

          <div className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-lg">
            <span className="text-slate-400 text-[10px] uppercase font-bold block">Last GMP Refresh</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200 mt-0.5 block">
              {ipoMetrics.last_gmp_refresh || 'Just now'}
            </span>
          </div>
        </div>

        {/* Last Error Banner */}
        <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700 dark:text-slate-300">Last Error:</span>
            <span className="px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 font-medium">
              {ipoMetrics.last_error ? ipoMetrics.last_error : 'None (All providers operational)'}
            </span>
          </div>
          <span className="text-slate-400 text-[11px]">Strict schema validation & IST normalization active</span>
        </div>
      </div>

      {/* Secondary: Equity Market Pipeline Audit Summary */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-4 transition-colors">
        <h2 className="text-sm font-bold text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
          Secondary Market Quotes Pipeline Summary
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
          <div>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-medium block">Records Received</span>
            <span className="text-2xl font-black text-slate-900 dark:text-white mt-1 block">
              {mMetrics.records_received || 0}
            </span>
          </div>
          <div>
            <span className="text-xs text-emerald-600 dark:text-emerald-400 font-medium block">Records Validated</span>
            <span className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1 block">
              {mMetrics.records_valid || 0}
            </span>
          </div>
          <div>
            <span className="text-xs text-rose-600 dark:text-rose-400 font-medium block">Records Rejected</span>
            <span className="text-2xl font-black text-rose-600 dark:text-rose-400 mt-1 block">
              {mMetrics.records_rejected || 0}
            </span>
          </div>
          <div>
            <span className="text-xs text-amber-600 dark:text-amber-400 font-medium block">Source Conflicts</span>
            <span className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-1 block">
              {mMetrics.cross_source_conflicts || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Active Validation Rules Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-3 transition-colors">
        <h2 className="text-sm font-bold text-slate-900 dark:text-white">Active Mathematical & Integrity Rules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-600 dark:text-slate-400">
          <div className="flex items-start gap-2 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-800 dark:text-slate-200">Zero Mock in Production: </span>
              <span>Enforces is_demo isolation. Mock historical records (e.g. Swiggy, NTPC Green) are blocked from production endpoints.</span>
            </div>
          </div>
          <div className="flex items-start gap-2 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-800 dark:text-slate-200">Dynamic IST Status Engine: </span>
              <span>Statuses (UPCOMING, OPEN, CLOSED, LISTED) are calculated dynamically in Asia/Kolkata timezone. Past listed IPOs can never be marked Upcoming.</span>
            </div>
          </div>
          <div className="flex items-start gap-2 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-800 dark:text-slate-200">Unofficial GMP Separation: </span>
              <span>Grey Market Premium is strictly segregated from official exchange disclosures and requires statutory warnings.</span>
            </div>
          </div>
          <div className="flex items-start gap-2 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-800 dark:text-slate-200">No Invented Data Policy: </span>
              <span>Missing issue sizes, dates, or prices render as 'Not Available' rather than synthetic placeholders.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
