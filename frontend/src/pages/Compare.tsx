import React, { useState, useEffect } from 'react';
import { 
  ArrowRightLeft, Layers, PieChart, Plus, Trash2, 
  RotateCcw, AlertCircle, ShieldAlert, CheckCircle2, ExternalLink 
} from 'lucide-react';
import { compareStocks, compareIPOs } from '../api/client';
import { SearchableStockSelector, StockOption } from '../components/SearchableStockSelector';
import { SearchableIPOSelector, IPOOption } from '../components/SearchableIPOSelector';

export const Compare: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'stocks' | 'ipos'>('ipos');

  // Stocks Compare State
  const [stockSymbols, setStockSymbols] = useState<string[]>(['RELIANCE', 'TCS', 'HDFCBANK']);
  const [stockData, setStockData] = useState<any[]>([]);
  const [stockLoading, setStockLoading] = useState<boolean>(false);

  // IPO Compare State (Strict Section 8 Compliance: 0 preloaded by default)
  const [selectedIPOs, setSelectedIPOs] = useState<(IPOOption | null)[]>([null, null]);
  const [ipoComparisonData, setIpoComparisonData] = useState<any[]>([]);
  const [ipoLoading, setIpoLoading] = useState<boolean>(false);
  const [demoMode, setDemoMode] = useState<boolean>(false);

  // Load Stock comparison
  const loadStockComparison = async () => {
    const validSymbols = stockSymbols.filter((s) => s.trim().length > 0);
    if (validSymbols.length === 0) {
      setStockData([]);
      return;
    }
    setStockLoading(true);
    try {
      const res = await compareStocks(validSymbols.join(','));
      setStockData(res.comparison || []);
    } catch (err) {
      console.error("Stock comparison failed", err);
      setStockData([]);
    } finally {
      setStockLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'stocks') {
      loadStockComparison();
    }
  }, [activeTab, stockSymbols]);

  // Load IPO comparison when selected IPOs change
  useEffect(() => {
    const validIds = selectedIPOs.filter((x): x is IPOOption => x !== null).map((x) => x.id);
    if (validIds.length < 2) {
      setIpoComparisonData([]);
      return;
    }

    const fetchComparison = async () => {
      setIpoLoading(true);
      try {
        const res = await compareIPOs(validIds.join(','));
        setIpoComparisonData(res.ipos || []);
      } catch (err) {
        console.error("Failed to load IPO comparison", err);
        setIpoComparisonData([]);
      } finally {
        setIpoLoading(false);
      }
    };

    fetchComparison();
  }, [selectedIPOs]);

  // Handle IPO Selector Controls
  const handleAddIPOSelector = () => {
    if (selectedIPOs.length < 5) {
      setSelectedIPOs([...selectedIPOs, null]);
    }
  };

  const handleRemoveIPOSelector = (index: number) => {
    if (selectedIPOs.length > 2) {
      const updated = [...selectedIPOs];
      updated.splice(index, 1);
      setSelectedIPOs(updated);
    } else {
      // Just clear the slot
      const updated = [...selectedIPOs];
      updated[index] = null;
      setSelectedIPOs(updated);
    }
  };

  const handleSelectIPO = (index: number, ipo: IPOOption) => {
    const updated = [...selectedIPOs];
    updated[index] = ipo;
    setSelectedIPOs(updated);
  };

  const handleClearAllIPOs = () => {
    setSelectedIPOs([null, null]);
    setIpoComparisonData([]);
  };

  // Helper formatting function for missing values (Strict: display Not available, never 0 or fake estimate)
  const formatCell = (val: any, prefix = '', suffix = '') => {
    if (val === null || val === undefined || val === '' || val === 'Not available' || val === 'N/A') {
      return <span className="text-slate-400 dark:text-slate-500 font-mono text-xs">Not available</span>;
    }
    return (
      <span className="font-semibold text-slate-800 dark:text-slate-200">
        {prefix}{typeof val === 'number' ? val.toLocaleString('en-IN') : val}{suffix}
      </span>
    );
  };

  const activeIPOCount = selectedIPOs.filter(Boolean).length;

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs transition-colors">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <ArrowRightLeft className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
                Factual Side-by-Side Comparison Engine
              </h1>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Objective parameter comparison across valuation, issue sizes, subscriptions, and fundamentals.
            </p>
          </div>

          {/* Toggle between Stocks & IPOs */}
          <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('ipos')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                activeTab === 'ipos' 
                  ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-xs' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <PieChart className="w-3.5 h-3.5" />
              <span>IPO Comparison</span>
            </button>
            <button
              onClick={() => setActiveTab('stocks')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                activeTab === 'stocks' 
                  ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-xs' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Stocks Comparison</span>
            </button>
          </div>
        </div>
      </div>

      {activeTab === 'ipos' ? (
        <div className="space-y-6">
          {/* Section 8: Select IPOs to Compare Controls */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 mb-5 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                  Select IPOs to Compare
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  Select 2 to 5 Mainboard or SME issues to inspect side-by-side metrics.
                </p>
              </div>

              <div className="flex items-center gap-2">
                {selectedIPOs.length < 5 && (
                  <button
                    onClick={handleAddIPOSelector}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded-lg text-xs font-semibold transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>+ Add IPO ({selectedIPOs.length}/5)</span>
                  </button>
                )}

                {activeIPOCount > 0 && (
                  <button
                    onClick={handleClearAllIPOs}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-lg text-xs font-semibold transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Clear All</span>
                  </button>
                )}
              </div>
            </div>

            {/* Selector Grid (2 to 5 searchable boxes) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
              {selectedIPOs.map((ipo, idx) => (
                <SearchableIPOSelector
                  key={idx}
                  selectorIndex={idx}
                  selectedIPO={ipo}
                  onSelect={(selected) => handleSelectIPO(idx, selected)}
                  onRemove={() => handleRemoveIPOSelector(idx)}
                  canRemove={selectedIPOs.length > 2 || ipo !== null}
                  demoMode={demoMode}
                />
              ))}
            </div>
          </div>

          {/* Comparison Presentation State */}
          {activeIPOCount === 0 ? (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-12 text-center shadow-xs">
              <PieChart className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
              <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">Select 2 to 5 IPOs to compare</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto mt-1">
                Select 2 to 5 IPOs using the search boxes above to view side-by-side financial metrics, timeline disclosures, and subscription data.
              </p>
            </div>
          ) : activeIPOCount === 1 ? (
            <div className="bg-white dark:bg-slate-900 border border-amber-200 dark:border-amber-900/40 rounded-xl p-8 text-center shadow-xs">
              <AlertCircle className="w-8 h-8 text-amber-500 mx-auto mb-2" />
              <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">Select at least 2 IPOs to compare</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                You have selected 1 IPO. Please select another issue in IPO Slot 2 to unlock comparison table.
              </p>
            </div>
          ) : ipoLoading ? (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-12 text-center">
              <div className="w-8 h-8 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
              <p className="text-xs text-slate-500 dark:text-slate-400">Loading verified comparative facts...</p>
            </div>
          ) : (
            /* Section 10: IPO Compare Table */
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
              {/* Unofficial GMP Statutory Separation Header Notice */}
              <div className="p-3 bg-amber-50 dark:bg-amber-950/30 border-b border-amber-200 dark:border-amber-900/40 flex items-center justify-between text-xs text-amber-900 dark:text-amber-200 px-6">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
                  <span>
                    <strong>Statutory Note:</strong> Official issue parameters are sourced from SEBI RHP & Exchange filings. GMP is strictly unofficial secondary sentiment.
                  </span>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-50 dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-slate-200 dark:border-slate-800">
                    <tr>
                      <th className="py-3 px-6 w-56 sticky left-0 bg-slate-50 dark:bg-slate-800/80 z-10">
                        Parameter
                      </th>
                      {ipoComparisonData.map((ipo) => (
                        <th key={ipo.id} className="py-3 px-6 text-right min-w-[200px]">
                          <span className="font-bold text-slate-900 dark:text-white text-sm block">
                            {ipo.company_name}
                          </span>
                          <span className="text-[11px] text-slate-500 dark:text-slate-400 font-normal">
                            {ipo.symbol || 'No Ticker'} • {ipo.board || 'Mainboard'}
                          </span>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                    {/* Status & Classification */}
                    <tr className="bg-slate-50/50 dark:bg-slate-800/20">
                      <td colSpan={ipoComparisonData.length + 1} className="py-2 px-6 font-bold text-[11px] text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                        1. Issue Structure & Classification
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Current Verified Status</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200">
                            {ipo.status}
                          </span>
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Exchange Board</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.board)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Trading Exchange</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.exchange)}</td>
                      ))}
                    </tr>

                    {/* Pricing & Issue Sizing */}
                    <tr className="bg-slate-50/50 dark:bg-slate-800/20">
                      <td colSpan={ipoComparisonData.length + 1} className="py-2 px-6 font-bold text-[11px] text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                        2. Pricing, Lot & Issue Sizing
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Issue Price</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right font-bold text-slate-800 dark:text-slate-200">
                          {formatCell(ipo.issue_price ? `₹${ipo.issue_price}` : (ipo.price_band_high ? `₹${ipo.price_band_high}` : null))}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Price Band</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.price_band)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Total Issue Size (₹ Cr)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.issue_size_crore, '₹', ' Cr')}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Lot Size (Shares)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.lot_size)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Fresh Issue (₹ Cr)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.fresh_issue_crore, '₹', ' Cr')}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Offer for Sale (OFS) (₹ Cr)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.offer_for_sale_crore, '₹', ' Cr')}</td>
                      ))}
                    </tr>

                    {/* Verified Lifecycle Dates */}
                    <tr className="bg-slate-50/50 dark:bg-slate-800/20">
                      <td colSpan={ipoComparisonData.length + 1} className="py-2 px-6 font-bold text-[11px] text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                        3. Verified Lifecycle Dates (Asia/Kolkata)
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Issue Open Date</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.open_date ? String(ipo.open_date).slice(0, 10) : null)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Issue Close Date</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.close_date ? String(ipo.close_date).slice(0, 10) : null)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Exchange Listing Date</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.listing_date ? String(ipo.listing_date).slice(0, 10) : null)}</td>
                      ))}
                    </tr>

                    {/* Official Subscription Times */}
                    <tr className="bg-slate-50/50 dark:bg-slate-800/20">
                      <td colSpan={ipoComparisonData.length + 1} className="py-2 px-6 font-bold text-[11px] text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                        4. Official Bidding Subscription (Times)
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Total Subscription</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right font-bold text-emerald-600 dark:text-emerald-400">
                          {formatCell(ipo.total_subscription, '', 'x')}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">QIB Quota</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.qib_subscription, '', 'x')}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">NII / HNI Quota</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.nii_subscription, '', 'x')}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Retail Quota</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.retail_subscription, '', 'x')}</td>
                      ))}
                    </tr>

                    {/* Unofficial GMP Section */}
                    <tr className="bg-slate-50/50 dark:bg-slate-800/20">
                      <td colSpan={ipoComparisonData.length + 1} className="py-2 px-6 font-bold text-[11px] text-amber-700 dark:text-amber-400 uppercase tracking-wider">
                        5. Listing Discovery & Unofficial Sentiment
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Actual Listing Price</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">
                          {ipo.actual_listing_price ? (
                            <span className="font-bold text-purple-600 dark:text-purple-400">
                              ₹{ipo.actual_listing_price}
                            </span>
                          ) : (
                            <span className="text-slate-400 dark:text-slate-500 font-mono text-xs">Not available</span>
                          )}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Listing Day Close</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">
                          {ipo.listing_day_close ? (
                            <span className="font-bold text-slate-900 dark:text-white">
                              ₹{ipo.listing_day_close}
                            </span>
                          ) : (
                            <span className="text-slate-400 dark:text-slate-500 font-mono text-xs">Not available</span>
                          )}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Historical GMP (Unofficial)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">
                          {ipo.gmp !== null && ipo.gmp !== undefined ? (
                            <span className={`font-bold ${ipo.gmp >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                              ₹{ipo.gmp} ({ipo.gmp_percent || 0}%)
                            </span>
                          ) : (
                            <span className="text-slate-400 dark:text-slate-500 font-mono text-xs">Not available</span>
                          )}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Estimated Listing Price (Indicative estimate)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">
                          {ipo.indicative_listing_price || ipo.estimated_listing_price ? (
                            <span className="font-semibold text-slate-800 dark:text-slate-200">
                              ₹{ipo.indicative_listing_price || ipo.estimated_listing_price}
                            </span>
                          ) : (
                            <span className="text-slate-400 dark:text-slate-500 font-mono text-xs">Not available</span>
                          )}
                        </td>
                      ))}
                    </tr>

                    {/* Fundamentals */}
                    <tr className="bg-slate-50/50 dark:bg-slate-800/20">
                      <td colSpan={ipoComparisonData.length + 1} className="py-2 px-6 font-bold text-[11px] text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                        6. Verified Financials (Official Prospectus)
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Revenue (₹ Cr)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.revenue, '₹', ' Cr')}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Net Profit (₹ Cr)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.profit, '₹', ' Cr')}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">EPS (₹)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.eps, '₹')}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">P/E Ratio</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.pe || ipo.pe_ratio)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Total Debt (₹ Cr)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.debt, '₹', ' Cr')}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Return on Equity (ROE %)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.roe, '', '%')}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">ROCE (%)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right">{formatCell(ipo.roce, '', '%')}</td>
                      ))}
                    </tr>

                    {/* Provenance */}
                    <tr className="bg-slate-50/50 dark:bg-slate-800/20">
                      <td colSpan={ipoComparisonData.length + 1} className="py-2 px-6 font-bold text-[11px] text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                        7. Official Provenance & Last Verification
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Verified Source</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right text-[11px]">
                          {ipo.source_url ? (
                            <a 
                              href={ipo.source_url} 
                              target="_blank" 
                              rel="noreferrer" 
                              className="text-emerald-600 dark:text-emerald-400 hover:underline inline-flex items-center gap-1 ml-auto"
                            >
                              <span>{ipo.source}</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          ) : (
                            formatCell(ipo.source)
                          )}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Last Verified (IST)</td>
                      {ipoComparisonData.map((ipo) => (
                        <td key={ipo.id} className="py-2.5 px-6 text-right text-[11px] text-slate-500 dark:text-slate-400">
                          {formatCell(ipo.last_verified_at)}
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Stocks Compare Tab (Section 15 Compliance) */
        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
            <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-1">
              Select Listed Equities to Compare
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              Search and compare active stocks using the searchable combobox.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {stockSymbols.map((sym, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-400">Stock {idx + 1}</span>
                    {stockSymbols.length > 2 && (
                      <button
                        onClick={() => {
                          const updated = [...stockSymbols];
                          updated.splice(idx, 1);
                          setStockSymbols(updated);
                        }}
                        className="text-[10px] text-rose-500 hover:underline"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <SearchableStockSelector
                    value={sym}
                    onChange={(newSym) => {
                      const updated = [...stockSymbols];
                      updated[idx] = newSym;
                      setStockSymbols(updated);
                    }}
                  />
                </div>
              ))}

              {stockSymbols.length < 5 && (
                <div className="flex items-end">
                  <button
                    onClick={() => setStockSymbols([...stockSymbols, ''])}
                    className="w-full py-2.5 px-3 border border-dashed border-slate-300 dark:border-slate-700 hover:border-emerald-500 rounded-lg text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-emerald-600 flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>+ Add Stock</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Stocks Table */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
            {stockLoading ? (
              <div className="p-12 text-center">
                <div className="w-8 h-8 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                <p className="text-xs text-slate-500 dark:text-slate-400">Loading equity comparison...</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-50 dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-slate-200 dark:border-slate-800">
                    <tr>
                      <th className="py-3 px-6 w-48">Parameter</th>
                      {stockData.map((s) => (
                        <th key={s.symbol} className="py-3 px-6 text-right min-w-[180px]">
                          <span className="font-bold text-slate-900 dark:text-white block text-sm">{s.symbol}</span>
                          <span className="text-[11px] text-slate-400 font-normal">{s.sector || 'NSE/BSE'}</span>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Current Market Price</td>
                      {stockData.map((s) => (
                        <td key={s.symbol} className="py-2.5 px-6 text-right font-bold text-slate-900 dark:text-white">
                          {s.current_price && s.current_price > 0 ? `₹${s.current_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : 'N/A'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Price-to-Earnings (P/E)</td>
                      {stockData.map((s) => (
                        <td key={s.symbol} className="py-2.5 px-6 text-right font-semibold text-slate-800 dark:text-slate-200">
                          {s.pe_ratio ? `${s.pe_ratio}x` : 'N/A'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Price-to-Book (P/B)</td>
                      {stockData.map((s) => (
                        <td key={s.symbol} className="py-2.5 px-6 text-right font-semibold text-slate-800 dark:text-slate-200">
                          {s.pb_ratio ? `${s.pb_ratio}x` : 'N/A'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Return on Equity (ROE)</td>
                      {stockData.map((s) => (
                        <td key={s.symbol} className="py-2.5 px-6 text-right font-semibold text-slate-800 dark:text-slate-200">
                          {s.roe ? `${s.roe}%` : 'N/A'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Debt to Equity</td>
                      {stockData.map((s) => (
                        <td key={s.symbol} className="py-2.5 px-6 text-right font-semibold text-slate-800 dark:text-slate-200">
                          {s.debt_to_equity !== undefined && s.debt_to_equity !== null ? s.debt_to_equity : 'N/A'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Annual Revenue (₹ Cr)</td>
                      {stockData.map((s) => (
                        <td key={s.symbol} className="py-2.5 px-6 text-right font-semibold text-slate-800 dark:text-slate-200">
                          {s.revenue ? `₹${s.revenue.toLocaleString('en-IN')} Cr` : 'N/A'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2.5 px-6 font-semibold text-slate-600 dark:text-slate-400">Net Profit (₹ Cr)</td>
                      {stockData.map((s) => (
                        <td key={s.symbol} className="py-2.5 px-6 text-right font-semibold text-slate-800 dark:text-slate-200">
                          {s.net_profit ? `₹${s.net_profit.toLocaleString('en-IN')} Cr` : 'N/A'}
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Compare;
