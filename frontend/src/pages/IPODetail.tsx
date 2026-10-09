import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  fetchIPODetail, fetchIPOCalculator, toggleIPOWatchlist 
} from '../api/client';
import { 
  PieChart, ShieldAlert, Sparkles, Building, Calendar, 
  Users, DollarSign, Activity, AlertCircle, ArrowLeft,
  Calculator, Bookmark, BookmarkCheck, ExternalLink,
  CheckCircle2, Clock, FileText, Bell, AlertTriangle,
  TrendingUp, TrendingDown, Layers, HelpCircle
} from 'lucide-react';

export const IPODetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Watchlist State
  const [isBookmarked, setIsBookmarked] = useState<boolean>(false);
  const [bookmarkLoading, setBookmarkLoading] = useState<boolean>(false);

  // Browser Notification Alert State
  const [alertsEnabled, setAlertsEnabled] = useState<boolean>(false);

  // Calculator State
  const [calcInvestment, setCalcInvestment] = useState<number>(15000);
  const [calcCustomPrice, setCalcCustomPrice] = useState<number | ''>('');
  const [calcResult, setCalcResult] = useState<any>(null);
  const [calcLoading, setCalcLoading] = useState<boolean>(false);

  useEffect(() => {
    const loadDetail = async () => {
      if (!id) return;
      setLoading(true);
      setErrorMsg(null);
      try {
        const res = await fetchIPODetail(id);
        setData(res);
        if (res?.ipo?.price_band_high) {
          setCalcCustomPrice(res.ipo.price_band_high);
        }
      } catch (err: any) {
        console.error("Error loading IPO detail", err);
        setErrorMsg("Failed to load verified IPO details. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    loadDetail();
  }, [id]);

  // Run calculator when inputs change
  useEffect(() => {
    const runCalc = async () => {
      if (!id) return;
      setCalcLoading(true);
      try {
        const priceArg = typeof calcCustomPrice === 'number' ? calcCustomPrice : undefined;
        const res = await fetchIPOCalculator(id, calcInvestment, priceArg);
        setCalcResult(res);
      } catch (err) {
        console.error("Calculator calculation failed", err);
      } finally {
        setCalcLoading(false);
      }
    };
    if (data?.ipo) {
      runCalc();
    }
  }, [id, data?.ipo, calcInvestment, calcCustomPrice]);

  const handleToggleWatchlist = async () => {
    if (!id) return;
    setBookmarkLoading(true);
    try {
      const res = await toggleIPOWatchlist(id);
      setIsBookmarked(res.is_bookmarked);
    } catch (err) {
      console.error("Failed to toggle watchlist", err);
    } finally {
      setBookmarkLoading(false);
    }
  };

  const handleToggleAlerts = async () => {
    if (!alertsEnabled) {
      if ('Notification' in window) {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          setAlertsEnabled(true);
          new Notification(`IPO Alert Enabled`, {
            body: `You will receive updates for ${data?.ipo?.company_name || 'this IPO'}.`
          });
        } else {
          alert('Notification permission was denied in your browser settings.');
        }
      } else {
        alert('Browser notifications are not supported in your browser.');
      }
    } else {
      setAlertsEnabled(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-3 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (errorMsg || !data?.ipo) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 text-center text-slate-600 dark:text-slate-400">
        <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto mb-2" />
        <p className="font-semibold text-slate-800 dark:text-white mb-2">{errorMsg || 'IPO record not found.'}</p>
        <Link to="/ipos" className="text-xs text-emerald-600 dark:text-emerald-400 hover:underline">
          Return to IPO Center
        </Link>
      </div>
    );
  }

  const { 
    ipo, 
    timeline = [], 
    documents = [], 
    subscription, 
    subscription_history = [], 
    gmp_history = [], 
    financials, 
    ai_prediction, 
    disclaimers 
  } = data;

  const hasGmp = ipo.gmp !== null && ipo.gmp !== undefined;
  const isGmpPositive = hasGmp && ipo.gmp >= 0;
  const isListed = ipo.status === 'LISTED' || ipo.status === 'LISTING_TODAY';

  return (
    <div className="space-y-6">
      {/* Top Nav: Back Link, Watchlist and Alert Actions */}
      <div className="flex items-center justify-between">
        <Link 
          to="/ipos" 
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to IPO Center</span>
        </Link>

        <div className="flex items-center gap-2">
          {/* Watchlist Toggle */}
          <button
            onClick={handleToggleWatchlist}
            disabled={bookmarkLoading}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              isBookmarked 
                ? 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-300 dark:border-emerald-700 text-emerald-700 dark:text-emerald-300' 
                : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
            }`}
          >
            {isBookmarked ? <BookmarkCheck className="w-3.5 h-3.5 text-emerald-600" /> : <Bookmark className="w-3.5 h-3.5" />}
            <span>{isBookmarked ? 'In Watchlist' : 'Add to Watchlist'}</span>
          </button>

          {/* Browser Notification Alert Toggle */}
          <button
            onClick={handleToggleAlerts}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              alertsEnabled
                ? 'bg-blue-50 dark:bg-blue-950/60 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300'
                : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
            }`}
          >
            <Bell className={`w-3.5 h-3.5 ${alertsEnabled ? 'text-blue-600 animate-bounce' : ''}`} />
            <span>{alertsEnabled ? 'Alerts On' : 'Track Alerts'}</span>
          </button>
        </div>
      </div>

      {/* Main Header Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs transition-colors">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                {ipo.company_name}
              </h1>
              <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                {ipo.board || ipo.ipo_type || 'Mainboard'}
              </span>
              <span className={`px-2.5 py-0.5 rounded text-xs font-extrabold uppercase tracking-wider ${
                ipo.status === 'OPEN' 
                  ? 'bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 animate-pulse'
                  : ipo.status === 'UPCOMING'
                  ? 'bg-blue-100 dark:bg-blue-950/80 text-blue-800 dark:text-blue-300'
                  : ipo.status === 'LISTED'
                  ? 'bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-300'
                  : ipo.status === 'ALLOTMENT'
                  ? 'bg-indigo-100 dark:bg-indigo-950/80 text-indigo-800 dark:text-indigo-300'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
              }`}>
                {ipo.status}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400 mt-2">
              <span><strong>Symbol:</strong> {ipo.symbol || 'Not available'}</span>
              <span>•</span>
              <span><strong>ISIN:</strong> {ipo.isin || 'Not available'}</span>
              <span>•</span>
              <span><strong>Exchange:</strong> {ipo.exchange || 'NSE / BSE'}</span>
              <span>•</span>
              <span><strong>Sector:</strong> {ipo.sector || 'Not available'}</span>
            </div>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400 dark:text-slate-500 block font-medium">Total Issue Size</span>
            <span className="text-2xl font-black text-slate-900 dark:text-white">
              {ipo.issue_size ? `₹${ipo.issue_size} Cr` : 'Not available'}
            </span>
            <span className="text-[11px] text-slate-400 dark:text-slate-500 block">
              Lot Size: {ipo.lot_size ? `${ipo.lot_size} shares` : 'Not available'}
            </span>
          </div>
        </div>

        {/* Section 6 - Complete Issue Parameters Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mt-6 pt-6 border-t border-slate-100 dark:border-slate-800 text-xs">
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Price Band</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {ipo.price_band_low && ipo.price_band_high 
                ? `₹${ipo.price_band_low} – ₹${ipo.price_band_high}` 
                : ipo.price_band_high 
                ? `₹${ipo.price_band_high}` 
                : 'Not available'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Face Value</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {ipo.face_value ? `₹${ipo.face_value}` : 'Not available'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Fresh Issue</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {ipo.fresh_issue_crore ? `₹${ipo.fresh_issue_crore} Cr` : 'Not available'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Offer for Sale (OFS)</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {ipo.offer_for_sale_crore ? `₹${ipo.offer_for_sale_crore} Cr` : 'Not available'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Registrar</span>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mt-0.5 truncate" title={ipo.registrar_name || ipo.registrar}>
              {ipo.registrar_name || ipo.registrar || 'Not available'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Lead Managers</span>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mt-0.5 truncate" title={ipo.lead_managers}>
              {ipo.lead_managers || 'Not available'}
            </span>
          </div>
        </div>

        {/* Section 6 - Key Verified Milestone Dates Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 text-xs">
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Open Date</span>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mt-0.5">
              {ipo.open_date || ipo.issue_open_date || 'TBA'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Close Date</span>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mt-0.5">
              {ipo.close_date || ipo.issue_close_date || 'TBA'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Allotment Date</span>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mt-0.5">
              {ipo.allotment_date || 'Not available'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Refund Date</span>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mt-0.5">
              {ipo.refund_date || 'Not available'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Demat Credit</span>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mt-0.5">
              {ipo.demat_credit_date || 'Not available'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Listing Date</span>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mt-0.5">
              {ipo.listing_date || 'Not available'}
            </span>
          </div>
        </div>

        {/* Section 2 - Visible Source & Last Verified Provenance Bar */}
        <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span className="text-slate-700 dark:text-slate-300">
              <strong>Source:</strong> {ipo.source || 'NSE Official Portal & Regulatory Filings'}
            </span>
            {ipo.source_url && (
              <a 
                href={ipo.source_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-emerald-600 dark:text-emerald-400 hover:underline inline-flex items-center gap-0.5 text-[11px]"
              >
                <span>View Source</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
          <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400 text-[11px]">
            <span><strong>Last Verified:</strong> {ipo.last_verified_at || 'Verified Record'}</span>
            {ipo.fetched_at && <span><strong>Fetched:</strong> {ipo.fetched_at}</span>}
          </div>
        </div>
      </div>

      {/* Visual Timeline Stepper */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
        <div className="flex items-center gap-2 pb-3 mb-5 border-b border-slate-100 dark:border-slate-800">
          <Calendar className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          <h2 className="font-bold text-sm text-slate-900 dark:text-white">IPO Verified Event Timeline</h2>
          <span className="text-[11px] text-slate-400 dark:text-slate-500 ml-auto">Asia/Kolkata (IST)</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {timeline.map((step: any, idx: number) => (
            <div 
              key={idx}
              className={`p-3.5 rounded-xl border text-center transition-all ${
                step.current 
                  ? 'bg-emerald-50 dark:bg-emerald-950/50 border-emerald-500 ring-2 ring-emerald-500/20' 
                  : step.completed 
                  ? 'bg-slate-50 dark:bg-slate-800/80 border-slate-200 dark:border-slate-700' 
                  : 'bg-white dark:bg-slate-900 border-dashed border-slate-200 dark:border-slate-800 opacity-60'
              }`}
            >
              <div className="flex justify-center mb-2">
                {step.completed ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                ) : step.current ? (
                  <Clock className="w-5 h-5 text-emerald-600 dark:text-emerald-400 animate-spin" />
                ) : (
                  <div className="w-5 h-5 rounded-full border border-slate-300 dark:border-slate-600 flex items-center justify-center text-[10px] text-slate-400">
                    {idx + 1}
                  </div>
                )}
              </div>
              <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 block">
                {step.step}
              </span>
              <span className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 block">
                {step.date}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Unofficial GMP Tracker Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 gap-2">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-600 dark:text-amber-400" />
            <div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">Unofficial Grey Market Premium (GMP) Signals</h3>
              <span className="text-[10px] text-slate-400 dark:text-slate-500">Separated secondary data feed • Strictly unofficial</span>
            </div>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300">
            UNOFFICIAL GMP
          </span>
        </div>

        {/* Mandatory Warning Notice */}
        <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-950/40 rounded-lg border border-amber-200 dark:border-amber-800/60 flex items-start gap-2.5 text-xs text-amber-900 dark:text-amber-200">
          <AlertCircle className="w-4 h-4 shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
          <span>
            <strong>Notice:</strong> IPO GMP is unofficial and is not an exchange price. It is provided for informational purposes only.
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 my-5">
          <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-800">
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Historical GMP</span>
            <div className={`text-2xl font-black mt-1 ${isGmpPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
              {hasGmp ? `₹${ipo.gmp} (${ipo.gmp_percent || 0}%)` : 'Not available'}
            </div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 mt-1 block">
              Source: {ipo.gmp_source || 'Secondary Market Feed'}
            </span>
          </div>

          <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-800">
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Estimated Listing Price</span>
            <div className="text-2xl font-black text-slate-900 dark:text-white mt-1">
              {ipo.estimated_listing_price ? `₹${ipo.estimated_listing_price}` : 'Not available'}
            </div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 mt-1 block font-medium">
              Indicative estimate (Issue Price + GMP)
            </span>
          </div>

          <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-800">
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Reported GMP Range</span>
            <div className="text-2xl font-black text-slate-800 dark:text-slate-200 mt-1">
              {ipo.min_gmp && ipo.max_gmp ? `₹${ipo.min_gmp} – ₹${ipo.max_gmp}` : hasGmp ? `₹${ipo.gmp}` : 'Not available'}
            </div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 mt-1 block">
              Estimated per lot: {hasGmp && ipo.lot_size ? `₹${(ipo.gmp * ipo.lot_size).toLocaleString('en-IN')}` : 'Not available'}
            </span>
          </div>

          <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-800">
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Actual Listing Price</span>
            <div className="text-2xl font-black text-purple-600 dark:text-purple-400 mt-1">
              {ipo.actual_listing_price ? `₹${ipo.actual_listing_price}` : 'Not available'}
            </div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 mt-1 block">
              {isListed ? 'Verified Exchange Discovery' : 'Awaiting listing session'}
            </span>
          </div>
        </div>

        {/* Historical GMP Records Table */}
        {gmp_history.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
            <h4 className="text-xs font-bold text-slate-800 dark:text-slate-200 mb-2">Preserved Historical GMP Quotes</h4>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 dark:bg-slate-800/70 text-slate-500 dark:text-slate-400">
                  <tr>
                    <th className="p-2.5">Date</th>
                    <th className="p-2.5">GMP</th>
                    <th className="p-2.5">GMP %</th>
                    <th className="p-2.5">Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {gmp_history.map((gh: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                      <td className="p-2.5 font-medium text-slate-700 dark:text-slate-300">{gh.date}</td>
                      <td className="p-2.5 font-bold text-emerald-600 dark:text-emerald-400">₹{gh.gmp}</td>
                      <td className="p-2.5 text-slate-700 dark:text-slate-300">{gh.gmp_percent}%</td>
                      <td className="p-2.5 text-slate-400">{gh.source}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Subscription Breakdown & Educational Calculator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Subscription History & Breakdown (Section 10 Compliance) */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">Official Subscription History</h3>
            </div>
            <span className="text-[11px] text-slate-400 dark:text-slate-500">
              {subscription?.captured_at ? `Last updated: ${subscription.captured_at}` : 'Official Disclosure'}
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60">
              <span className="font-medium text-slate-700 dark:text-slate-300">QIB (Qualified Institutional)</span>
              <span className="font-bold text-slate-900 dark:text-white">
                {subscription?.qib !== null && subscription?.qib !== undefined ? `${subscription.qib}x` : 'Not Available'}
              </span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60">
              <span className="font-medium text-slate-700 dark:text-slate-300">NII (Non-Institutional / HNI)</span>
              <span className="font-bold text-slate-900 dark:text-white">
                {subscription?.nii !== null && subscription?.nii !== undefined ? `${subscription.nii}x` : 'Not Available'}
              </span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60">
              <span className="font-medium text-slate-700 dark:text-slate-300">Retail Individual Investors</span>
              <span className="font-bold text-slate-900 dark:text-white">
                {subscription?.retail !== null && subscription?.retail !== undefined ? `${subscription.retail}x` : 'Not Available'}
              </span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60">
              <span className="font-medium text-slate-700 dark:text-slate-300">Employee Quota</span>
              <span className="font-bold text-slate-900 dark:text-white">
                {subscription?.employee !== null && subscription?.employee !== undefined ? `${subscription.employee}x` : 'Not Available'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-900 dark:text-emerald-200 font-bold border border-emerald-200 dark:border-emerald-800">
              <span>Total Subscription Ratio</span>
              <span className="text-base">
                {subscription?.total !== null && subscription?.total !== undefined ? `${subscription.total}x` : 'Not Available'}
              </span>
            </div>
          </div>
        </div>

        {/* Educational Lot & Capital Calculator (Section 18 Compliance) */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
          <div className="flex items-center gap-2 pb-3 mb-4 border-b border-slate-100 dark:border-slate-800">
            <Calculator className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">Educational IPO Lot Calculator</h3>
          </div>

          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 block mb-1">
                  Investment Budget (₹)
                </label>
                <input
                  type="number"
                  value={calcInvestment}
                  onChange={(e) => setCalcInvestment(Math.max(0, Number(e.target.value)))}
                  className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2 font-bold text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 block mb-1">
                  Bidding Price (₹)
                </label>
                <input
                  type="number"
                  value={calcCustomPrice}
                  onChange={(e) => setCalcCustomPrice(e.target.value ? Number(e.target.value) : '')}
                  className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2 font-bold text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>
            </div>

            {calcResult && (
              <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-800 space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-slate-400">Lot Size:</span>
                  <span className="font-bold text-slate-900 dark:text-white">{calcResult.lot_size} shares/lot</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-slate-400">Price per Lot:</span>
                  <span className="font-bold text-slate-900 dark:text-white">₹{calcResult.price_per_lot?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between border-t border-slate-200 dark:border-slate-700 pt-2 font-bold">
                  <span className="text-emerald-700 dark:text-emerald-400">Affordable Lots:</span>
                  <span className="text-emerald-700 dark:text-emerald-400 text-sm">{calcResult.affordable_lots} Lots ({calcResult.total_shares} shares)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-slate-400">Capital Required:</span>
                  <span className="font-bold text-slate-900 dark:text-white">₹{calcResult.total_amount_required?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Unutilized Budget:</span>
                  <span>₹{calcResult.unutilized_balance?.toLocaleString('en-IN')}</span>
                </div>
              </div>
            )}

            <p className="text-[10px] text-slate-400 dark:text-slate-500 italic">
              Notice: This is an educational calculation of bidding tranches and does not predict or guarantee IPO allotment.
            </p>
          </div>
        </div>
      </div>

      {/* Verified Document Center (Section 21 Compliance) */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
        <div className="flex items-center gap-2 pb-3 mb-4 border-b border-slate-100 dark:border-slate-800">
          <FileText className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          <h3 className="font-bold text-sm text-slate-900 dark:text-white">Official Document & Filing Center</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {documents.map((doc: any, idx: number) => (
            <a
              key={idx}
              href={doc.url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-3.5 bg-slate-50 dark:bg-slate-800/60 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 rounded-xl border border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs transition-colors group"
            >
              <div>
                <span className="font-bold text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 block">
                  {doc.title}
                </span>
                <span className="text-[10px] text-slate-400 dark:text-slate-500">{doc.type} Verified Link</span>
              </div>
              <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-emerald-600 shrink-0 ml-2" />
            </a>
          ))}
        </div>
      </div>

      {/* Company Fundamentals Disclosures */}
      {financials && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
          <div className="flex items-center gap-2 pb-3 mb-4 border-b border-slate-100 dark:border-slate-800">
            <DollarSign className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">Audited Financial Disclosures (RHP)</h3>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl">
              <span className="text-[10px] text-slate-400 font-medium">Revenue</span>
              <span className="font-bold text-slate-900 dark:text-white block mt-0.5">
                {financials.revenue ? `₹${financials.revenue} Cr` : 'Not Disclosed'}
              </span>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl">
              <span className="text-[10px] text-slate-400 font-medium">Net Profit</span>
              <span className={`font-bold block mt-0.5 ${financials.profit >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                {financials.profit ? `₹${financials.profit} Cr` : 'Not Disclosed'}
              </span>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl">
              <span className="text-[10px] text-slate-400 font-medium">EPS</span>
              <span className="font-bold text-slate-900 dark:text-white block mt-0.5">
                {financials.eps ? `₹${financials.eps}` : 'Not Disclosed'}
              </span>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl">
              <span className="text-[10px] text-slate-400 font-medium">Total Debt</span>
              <span className="font-bold text-slate-900 dark:text-white block mt-0.5">
                {financials.debt !== null && financials.debt !== undefined ? `₹${financials.debt} Cr` : 'Not Disclosed'}
              </span>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl">
              <span className="text-[10px] text-slate-400 font-medium">ROE</span>
              <span className="font-bold text-slate-900 dark:text-white block mt-0.5">
                {financials.roe ? `${financials.roe}%` : 'Not Disclosed'}
              </span>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl">
              <span className="text-[10px] text-slate-400 font-medium">ROCE</span>
              <span className="font-bold text-slate-900 dark:text-white block mt-0.5">
                {financials.roce ? `${financials.roce}%` : 'Not Disclosed'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Disclaimers Footer */}
      <div className="text-[11px] text-slate-400 dark:text-slate-500 bg-slate-50 dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
        <p><strong>Disclaimer:</strong> {disclaimers?.financial_disclaimer || "Information presented is for educational purposes only and not investment advice."}</p>
        <p><strong>GMP Disclaimer:</strong> {disclaimers?.gmp_warning}</p>
      </div>
    </div>
  );
};
