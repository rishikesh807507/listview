import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  PieChart, Filter, Search, Calendar, ShieldAlert, 
  ArrowUpRight, ArrowDownRight, ChevronRight, Layers, 
  RefreshCw, CheckCircle2, Clock, Info, AlertTriangle,
  Building, ExternalLink, Bookmark, ArrowUpDown
} from 'lucide-react';
import { fetchIPOs, refreshIPOs } from '../api/client';

export const IPOCenter: React.FC = () => {
  const [ipos, setIpos] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [boardFilter, setBoardFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('open_date');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');
  const [search, setSearch] = useState<string>('');
  const [demoMode, setDemoMode] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadIPOs = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const data = await fetchIPOs({
        status: statusFilter !== 'all' ? statusFilter : undefined,
        board: boardFilter !== 'all' ? boardFilter : undefined,
        search: search.trim() || undefined,
        sort_by: sortBy || undefined,
        sort_order: sortOrder,
        mode: demoMode ? 'demo' : 'live'
      });
      setIpos(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error("Error loading IPOs", err);
      setErrorMsg("Live IPO data temporarily unavailable. Showing last verified cache if present.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadIPOs();
    }, 200);
    return () => clearTimeout(timer);
  }, [statusFilter, boardFilter, search, sortBy, sortOrder, demoMode]);

  const handleManualRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshIPOs();
      await loadIPOs();
    } catch (err) {
      console.error("Failed to refresh IPOs", err);
    } finally {
      setRefreshing(false);
    }
  };

  const statusTabs = [
    { id: 'all', label: 'All' },
    { id: 'UPCOMING', label: 'Upcoming' },
    { id: 'OPEN', label: 'Open' },
    { id: 'CLOSED', label: 'Closed' },
    { id: 'ALLOTMENT', label: 'Allotment' },
    { id: 'LISTING', label: 'Listing' },
    { id: 'LISTED', label: 'Listed' }
  ];

  return (
    <div className="space-y-6">
      {/* Demo Mode Banner */}
      {demoMode && (
        <div className="bg-amber-500 text-slate-950 px-4 py-2.5 rounded-xl font-bold flex items-center justify-between text-xs shadow-md">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>DEMO MODE ACTIVE: Showing mock & historical demonstration records. Switch back to Production for verified live data.</span>
          </div>
          <button 
            onClick={() => setDemoMode(false)}
            className="px-2.5 py-1 bg-slate-950 text-white rounded text-[11px] hover:bg-slate-800 transition-colors"
          >
            Switch to Production
          </button>
        </div>
      )}

      {/* Header Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs transition-colors">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <PieChart className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
                Indian IPO Intelligence & Disclosures
              </h1>
              <span className={`px-2 py-0.5 text-[11px] font-bold rounded-full ${
                demoMode 
                  ? 'bg-amber-100 text-amber-900 dark:bg-amber-950/80 dark:text-amber-300' 
                  : 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-300'
              }`}>
                {demoMode ? 'DEMO DATA' : 'EXCHANGE DISCLOSURES'}
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Tracking Mainboard and SME public issues via public exchange disclosures, schedule validation, and separate unofficial GMP signals.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleManualRefresh}
              disabled={refreshing}
              className="px-3.5 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
              title="Refresh from official exchange sources"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
              <span>{refreshing ? 'Refreshing...' : 'Sync Exchanges'}</span>
            </button>

            <Link
              to="/gmp"
              className="px-3.5 py-1.5 bg-emerald-50 dark:bg-emerald-950/50 hover:bg-emerald-100 dark:hover:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 rounded-lg text-xs font-semibold border border-emerald-200 dark:border-emerald-800 flex items-center gap-1.5 transition-colors"
            >
              <ShieldAlert className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span>Unofficial GMP Tracker</span>
            </Link>

            <button
              onClick={() => setDemoMode(!demoMode)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${
                demoMode 
                  ? 'bg-amber-100 dark:bg-amber-950/60 border-amber-300 text-amber-800 dark:text-amber-300' 
                  : 'bg-slate-50 dark:bg-slate-800/80 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'
              }`}
            >
              {demoMode ? 'Exit Demo' : 'Review Demo Data'}
            </button>
          </div>
        </div>

        {/* Filters Row */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 mt-6 pt-5 border-t border-slate-100 dark:border-slate-800">
          {/* Status Tabs */}
          <div className="flex flex-wrap items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
            {statusTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                  statusFilter === tab.id
                    ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Board, Sorting & Search */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Board Selector */}
            <select
              value={boardFilter}
              onChange={(e) => setBoardFilter(e.target.value)}
              className="text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500 font-medium"
            >
              <option value="all">All Boards</option>
              <option value="Mainboard">Mainboard</option>
              <option value="SME">SME Exchange</option>
            </select>

            {/* Sort Dropdown */}
            <div className="flex items-center gap-1 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1">
              <span className="text-[10px] text-slate-400 uppercase font-bold">Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="text-xs bg-transparent border-none text-slate-700 dark:text-slate-200 focus:outline-none font-medium pr-1"
              >
                <option value="open_date">Open Date</option>
                <option value="close_date">Close Date</option>
                <option value="listing_date">Listing Date</option>
                <option value="issue_size">Issue Size</option>
                <option value="subscription">Subscription</option>
              </select>
              <button
                type="button"
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-500"
                title={`Order: ${sortOrder.toUpperCase()}`}
              >
                <ArrowUpDown className="w-3 h-3" />
              </button>
            </div>

            {/* Search Input */}
            <div className="relative flex-1 sm:w-56">
              <Search className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search IPO, symbol, ISIN..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full text-xs pl-8 pr-3 py-1.5 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory Unofficial GMP Disclaimer Banner */}
      <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 p-3 rounded-xl flex items-center gap-2.5 text-xs text-amber-900 dark:text-amber-200">
        <ShieldAlert className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
        <span>
          <strong>UNOFFICIAL GMP NOTICE:</strong> Grey Market Premium (GMP) is unofficial, unregulated, and sourced from grey market participants. It is not an NSE/BSE price and is not a guaranteed listing indicator.
        </span>
      </div>

      {/* Error state */}
      {errorMsg && (
        <div className="bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 p-3 rounded-xl flex items-center gap-2 text-xs text-rose-800 dark:text-rose-300">
          <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* IPOs Grid */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[30vh]">
          <div className="w-7 h-7 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : ipos.length === 0 ? (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-12 text-center text-slate-500 dark:text-slate-400 text-sm">
          <CheckCircle2 className="w-8 h-8 text-slate-300 dark:text-slate-700 mx-auto mb-2" />
          <p className="font-semibold text-slate-700 dark:text-slate-300">
            No verified IPOs currently match this filter.
          </p>
          <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
            Data accuracy is prioritized over placeholder records. All filtered categories reflect verified official exchange milestones.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {ipos.map((ipo) => {
            const hasGmp = ipo.gmp !== null && ipo.gmp !== undefined;
            const isGmpPositive = hasGmp && ipo.gmp >= 0;
            const isListed = ipo.status === 'LISTED' || ipo.status === 'LISTING_TODAY';

            return (
              <div
                key={ipo.id}
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs hover:border-emerald-300 dark:hover:border-emerald-700 transition-all flex flex-col justify-between"
              >
                <div>
                  {/* Top Bar: Exchange, Board & Dynamic Status Badge */}
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                          {ipo.exchange || 'NSE/BSE'} • {ipo.board || ipo.ipo_type || 'Mainboard'}
                        </span>
                        {ipo.is_demo && (
                          <span className="px-1.5 py-0.2 text-[9px] font-bold rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                            DEMO
                          </span>
                        )}
                      </div>
                      <Link 
                        to={`/ipos/${ipo.id}`} 
                        className="font-bold text-sm text-slate-900 dark:text-white hover:text-emerald-600 dark:hover:text-emerald-400 mt-0.5 block transition-colors"
                      >
                        {ipo.company_name}
                      </Link>
                      <span className="text-[11px] text-slate-500 dark:text-slate-400">
                        {ipo.symbol ? `${ipo.symbol} • ` : ''}{ipo.sector || 'Commercial & Industrial'}
                      </span>
                    </div>

                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      ipo.status === 'OPEN'
                        ? 'bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 animate-pulse'
                        : ipo.status === 'UPCOMING'
                        ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300'
                        : ipo.status === 'LISTED'
                        ? 'bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300'
                        : ipo.status === 'LISTING_TODAY'
                        ? 'bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 font-black'
                        : ipo.status === 'ALLOTMENT'
                        ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}>
                      {ipo.status}
                    </span>
                  </div>

                  {/* Card Body: Distinct Structure for LISTED vs UPCOMING/OPEN */}
                  {isListed ? (
                    <div className="mt-3 space-y-3">
                      {/* 4-Item Parameter Grid */}
                      <div className="grid grid-cols-2 gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 block font-medium">Issue Price</span>
                          <span className="font-bold text-slate-800 dark:text-slate-200">
                            {ipo.issue_price ? `₹${ipo.issue_price}` : (ipo.price_band_high ? `₹${ipo.price_band_high}` : 'Not available')}
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 block font-medium">Issue Size</span>
                          <span className="font-bold text-slate-800 dark:text-slate-200">
                            {ipo.issue_size ? `₹${ipo.issue_size} Cr` : 'Not available'}
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 block font-medium">Lot Size</span>
                          <span className="font-semibold text-slate-700 dark:text-slate-300">
                            {ipo.lot_size ? `${ipo.lot_size} Shares` : 'Not available'}
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 block font-medium">Listing Date</span>
                          <span className="font-semibold text-slate-700 dark:text-slate-300">
                            {ipo.listing_date || 'Not available'}
                          </span>
                        </div>
                      </div>

                      {/* Verified Exchange Prices & Historical GMP */}
                      <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-100 dark:border-slate-800 grid grid-cols-3 gap-2 text-xs">
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold block truncate">
                            Actual Listing Price
                          </span>
                          <span className="font-bold text-purple-700 dark:text-purple-300 block mt-0.5">
                            {ipo.actual_listing_price ? `₹${ipo.actual_listing_price}` : 'Not available'}
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold block truncate">
                            Listing Day Close
                          </span>
                          <span className="font-bold text-slate-900 dark:text-white block mt-0.5">
                            {ipo.listing_day_close ? `₹${ipo.listing_day_close}` : 'Not available'}
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold block truncate">
                            Historical GMP
                          </span>
                          <span className="font-bold text-slate-700 dark:text-slate-300 block mt-0.5">
                            {hasGmp ? `₹${ipo.gmp}` : 'Not available'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-3 space-y-3">
                      {/* Price & Size Grid for Non-Listed */}
                      <div className="grid grid-cols-2 gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 block font-medium">Price Band</span>
                          <span className="font-bold text-slate-800 dark:text-slate-200">
                            {ipo.price_band_low && ipo.price_band_high 
                              ? `₹${ipo.price_band_low} – ₹${ipo.price_band_high}` 
                              : ipo.price_band_high 
                              ? `₹${ipo.price_band_high}` 
                              : 'Not available'}
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 block font-medium">Issue Size</span>
                          <span className="font-bold text-slate-800 dark:text-slate-200">
                            {ipo.issue_size ? `₹${ipo.issue_size} Cr` : 'Not available'}
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 block font-medium">Lot Size</span>
                          <span className="font-semibold text-slate-700 dark:text-slate-300">
                            {ipo.lot_size ? `${ipo.lot_size} Shares` : 'Not available'}
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 block font-medium">Timeline</span>
                          <span className="font-semibold text-slate-700 dark:text-slate-300">
                            {ipo.open_date && ipo.close_date
                              ? `${ipo.open_date} – ${ipo.close_date}`
                              : ipo.open_date || 'TBA'}
                          </span>
                        </div>
                      </div>

                      {/* Unofficial GMP & Indicative Estimate */}
                      <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-100 dark:border-slate-800 flex items-center justify-between">
                        <div>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold uppercase tracking-wider block">
                            Unofficial GMP
                          </span>
                          <span className={`text-xs font-bold ${
                            hasGmp ? (isGmpPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400') : 'text-slate-500'
                          }`}>
                            {hasGmp ? `₹${ipo.gmp} (${ipo.gmp_percent || 0}%)` : 'Not available'}
                          </span>
                        </div>

                        <div className="text-right">
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold block" title="Indicative estimate: Upper price band + GMP">
                            Indicative estimate
                          </span>
                          <span className="text-xs font-bold text-slate-900 dark:text-white">
                            {ipo.estimated_listing_price ? `₹${ipo.estimated_listing_price}` : 'Not available'}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Card Footer: Subscription, Source Attribution & Detail Link */}
                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-500 dark:text-slate-400">
                      Subscription: <strong className="text-slate-800 dark:text-slate-200">{ipo.subscription_total ? `${ipo.subscription_total}x` : 'Not available'}</strong>
                    </span>
                    <span className="text-[10px] text-slate-400 dark:text-slate-500">
                      Source: {ipo.source || 'NSE'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[10px] text-slate-400 dark:text-slate-500">
                      {ipo.last_verified_at ? `Verified: ${ipo.last_verified_at}` : 'Source: NSE'}
                    </span>
                    <Link
                      to={`/ipos/${ipo.id}`}
                      className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 flex items-center gap-0.5"
                    >
                      <span>Full Analysis & Timeline</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
