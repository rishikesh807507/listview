import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { 
  fetchStockDetail, fetchStockHistory, fetchStockHealth, 
  fetchStockStatements, fetchStockPrediction, fetchNews, addToWatchlist 
} from '../api/client';
import { TradingViewChart } from '../components/TradingViewChart';
import { HealthScoreCard } from '../components/HealthScoreCard';
import { StatusBadge } from '../components/StatusBadge';
import { 
  TrendingUp, TrendingDown, Bookmark, Sparkles, Building2, 
  FileText, Activity, AlertCircle, Check 
} from 'lucide-react';

const isValidNumber = (val: any): boolean => {
  if (val === null || val === undefined || val === '') return false;
  const num = Number(val);
  return !isNaN(num) && isFinite(num);
};

export const StockDetail: React.FC = () => {
  const { symbol = 'RELIANCE' } = useParams<{ symbol: string }>();
  const [stockDetail, setStockDetail] = useState<any>(null);
  const [candles, setCandles] = useState<any[]>([]);
  const [healthData, setHealthData] = useState<any>(null);
  const [statements, setStatements] = useState<any>(null);
  const [prediction, setPrediction] = useState<any>(null);
  const [newsList, setNewsList] = useState<any[]>([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('1Y');
  const [statementTab, setStatementTab] = useState<'income' | 'balance_sheet' | 'cash_flow'>('income');
  const [loading, setLoading] = useState(true);
  const [watchlistAdded, setWatchlistAdded] = useState(false);

  useEffect(() => {
    let isCancelled = false;

    const loadStock = async () => {
      setLoading(true);
      setCandles([]);
      setStockDetail(null);
      setHealthData(null);
      setStatements(null);
      setPrediction(null);
      setNewsList([]);

      try {
        const [detail, history, health, stmt, pred, news] = await Promise.allSettled([
          fetchStockDetail(symbol),
          fetchStockHistory(symbol, selectedTimeframe),
          fetchStockHealth(symbol),
          fetchStockStatements(symbol),
          fetchStockPrediction(symbol),
          fetchNews({ symbol })
        ]);

        if (!isCancelled) {
          if (detail.status === 'fulfilled') setStockDetail(detail.value);
          if (history.status === 'fulfilled') setCandles(history.value?.candles || []);
          if (health.status === 'fulfilled') setHealthData(health.value);
          if (stmt.status === 'fulfilled') setStatements(stmt.value?.statements || {});
          if (pred.status === 'fulfilled') setPrediction(pred.value);
          if (news.status === 'fulfilled') setNewsList(news.value?.articles || []);
        }
      } catch (err) {
        console.error("Error loading stock detail", err);
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    loadStock();

    return () => {
      isCancelled = true;
    };
  }, [symbol]);

  const handleTimeframeChange = async (tf: string) => {
    setSelectedTimeframe(tf);
    try {
      const history = await fetchStockHistory(symbol, tf);
      setCandles(history?.candles || []);
    } catch (err) {
      console.error("Failed to fetch timeframe history", err);
    }
  };

  const handleAddToWatchlist = async () => {
    try {
      await addToWatchlist(symbol);
      setWatchlistAdded(true);
      setTimeout(() => setWatchlistAdded(false), 2500);
    } catch (err) {
      console.error("Failed to add to watchlist", err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-3 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-xs text-slate-500 font-medium">Retrieving financial records for {symbol}...</span>
        </div>
      </div>
    );
  }

  const stock = stockDetail?.stock;
  const hasPrice = isValidNumber(stock?.current_price);
  const hasChange = isValidNumber(stock?.change) && isValidNumber(stock?.change_percent);
  const isUp = hasChange ? Number(stock.change) >= 0 : true;

  return (
    <div className="space-y-6">
      {/* Fallback Notice Banner if external live API is degraded */}
      {stockDetail?.notice && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-2.5 rounded-xl text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>{stockDetail.notice}</span>
        </div>
      )}

      {/* Stock Header Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">{stock?.symbol || symbol}</h1>
              <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                {stock?.exchange || 'NSE'}
              </span>
              <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400">
                {stock?.sector || 'General'}
              </span>
              <StatusBadge
                status={stockDetail?.status}
                source={stockDetail?.source}
                lastUpdated={stockDetail?.last_updated}
              />
            </div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mt-1">{stock?.name || symbol}</p>
          </div>

          {/* Price & Action */}
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-3xl font-extrabold text-slate-900 dark:text-white">
                {hasPrice 
                  ? `₹${Number(stock.current_price).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` 
                  : 'N/A'}
              </div>
              {hasChange ? (
                <div className={`flex items-center justify-end gap-1 text-xs font-bold ${isUp ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                  {isUp ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span>{isUp ? '+' : ''}{Number(stock.change).toFixed(2)} ({isUp ? '+' : ''}{Number(stock.change_percent).toFixed(2)}%)</span>
                </div>
              ) : (
                <div className="text-xs font-medium text-slate-400">N/A</div>
              )}
            </div>

            <button
              onClick={handleAddToWatchlist}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                watchlistAdded
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300'
              }`}
            >
              {watchlistAdded ? <Check className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
              <span>{watchlistAdded ? 'Added' : 'Watchlist'}</span>
            </button>
          </div>
        </div>

        {/* Quick Fundamental Metrics Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 mt-6 pt-6 border-t border-slate-100 dark:border-slate-800">
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Mkt Cap (Cr)</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {isValidNumber(stock?.market_cap) && Number(stock.market_cap) > 0
                ? `₹${Number(stock.market_cap).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
                : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">P/E Ratio</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {isValidNumber(stock?.pe_ratio) && Number(stock.pe_ratio) > 0
                ? `${Number(stock.pe_ratio).toFixed(2)}x`
                : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">P/B Ratio</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {isValidNumber(stock?.pb_ratio) && Number(stock.pb_ratio) > 0
                ? `${Number(stock.pb_ratio).toFixed(2)}x`
                : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">ROE</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {isValidNumber(stock?.roe)
                ? `${Number(stock.roe).toFixed(2)}%`
                : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">ROCE</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {isValidNumber(stock?.roce)
                ? `${Number(stock.roce).toFixed(2)}%`
                : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Debt / Equity</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {isValidNumber(stock?.debt_to_equity)
                ? `${Number(stock.debt_to_equity).toFixed(2)}x`
                : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">52W Range</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {isValidNumber(stock?.low_52w) && isValidNumber(stock?.high_52w) && Number(stock.low_52w) > 0 && Number(stock.high_52w) > 0
                ? `₹${Number(stock.low_52w).toLocaleString('en-IN', { maximumFractionDigits: 2 })} - ₹${Number(stock.high_52w).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
                : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Div Yield</span>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
              {isValidNumber(stock?.dividend_yield) && Number(stock.dividend_yield) >= 0
                ? `${Number(stock.dividend_yield).toFixed(2)}%`
                : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Interactive TradingView Lightweight Chart */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-emerald-600" />
            <span>Interactive Technical Chart</span>
          </h2>
          <span className="text-xs text-slate-400">TradingView Lightweight Charts (Apache-2.0)</span>
        </div>
        <TradingViewChart
          candles={candles}
          symbol={stock?.symbol || symbol}
          selectedTimeframe={selectedTimeframe}
          onTimeframeChange={handleTimeframeChange}
        />
      </div>

      {/* AI Directional Prediction & Model Transparency */}
      {prediction && !prediction.error && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 gap-3">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-emerald-600" />
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">AI Directional & Return Forecast (Open-Source ML)</h3>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Validated using TimeSeriesSplit walk-forward splits to prevent lookahead and data leakage
              </p>
            </div>
            <span className="text-xs text-slate-400">Generated: {prediction.prediction_timestamp || 'N/A'}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 my-4">
            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Direction Probability</span>
              <div className="text-lg font-bold text-slate-900 dark:text-white mt-1">
                {isValidNumber(prediction.positive_prob) ? `${prediction.positive_prob}% Positive` : 'N/A'}
              </div>
              <span className="text-[10px] text-slate-500 dark:text-slate-400">{prediction.target_timeframe || '1-5 Trading Days'}</span>
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Expected Return Range</span>
              <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400 mt-1">
                {isValidNumber(prediction.expected_return_min) && isValidNumber(prediction.expected_return_max)
                  ? `${prediction.expected_return_min}% to +${prediction.expected_return_max}%`
                  : 'N/A'}
              </div>
              <span className="text-[10px] text-slate-500 dark:text-slate-400">
                {isValidNumber(prediction.volatility_annualized) ? `Vol: ${prediction.volatility_annualized}% p.a.` : ''}
              </span>
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Model & Validation</span>
              <div className="text-sm font-bold text-slate-900 dark:text-white mt-1">
                {prediction.model_name || 'RandomForest'}
              </div>
              <span className="text-[10px] text-slate-500 dark:text-slate-400">
                Accuracy: {isValidNumber(prediction.metrics?.walk_forward_accuracy) ? prediction.metrics.walk_forward_accuracy : 'N/A'}
              </span>
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Confidence Level</span>
              <div className="text-sm font-bold text-slate-900 dark:text-white mt-1">
                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                  prediction.confidence === 'High' ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300' : 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300'
                }`}>
                  {prediction.confidence || 'Moderate'} Confidence
                </span>
              </div>
              <span className="text-[10px] text-slate-500 dark:text-slate-400">
                F1: {isValidNumber(prediction.metrics?.f1_score) ? prediction.metrics.f1_score : 'N/A'} • MAE: {isValidNumber(prediction.metrics?.mae) ? prediction.metrics.mae : 'N/A'}
              </span>
            </div>
          </div>

          <div className="text-[11px] text-slate-400 bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded border border-slate-100 dark:border-slate-800 flex items-start gap-2">
            <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5 text-slate-400" />
            <span>{prediction.disclaimer}</span>
          </div>
        </div>
      )}

      {/* Fundamental Health Score Breakdown */}
      {healthData && (
        <HealthScoreCard
          score={healthData.score_out_of_100}
          overallHealth={healthData.overall_health}
          components={healthData.components}
          disclaimer={healthData.disclaimer}
        />
      )}

      {/* Multi-Year Financial Statements */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 gap-3">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-emerald-600" />
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">Financial Statements</h3>
          </div>

          {/* Statement Tabs */}
          <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
            {(['income', 'balance_sheet', 'cash_flow'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setStatementTab(tab)}
                className={`px-3 py-1 text-xs font-semibold rounded-md capitalize transition-colors ${
                  statementTab === tab ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                {tab.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Statement Table */}
        <div className="overflow-x-auto mt-4">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-slate-100 dark:border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Metric (₹ Cr)</th>
                {(statements?.[statementTab] || []).map((s: any) => (
                  <th key={s.year} className="py-2.5 px-3 text-right">FY {s.year}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {statements?.[statementTab]?.length > 0 &&
                Object.keys(statements[statementTab][0].metrics || {}).map((metricKey) => (
                  <tr key={metricKey} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40">
                    <td className="py-2 px-3 font-medium text-slate-700 dark:text-slate-300 capitalize">
                      {metricKey.replace(/_/g, ' ')}
                    </td>
                    {statements[statementTab].map((s: any) => (
                      <td key={s.year} className="py-2 px-3 text-right font-semibold text-slate-900 dark:text-white">
                        {isValidNumber(s.metrics[metricKey])
                          ? Number(s.metrics[metricKey]).toLocaleString('en-IN')
                          : 'N/A'}
                      </td>
                    ))}
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Related News & Sentiment */}
      {newsList.length > 0 && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
          <div className="flex items-center gap-2 pb-3 mb-3 border-b border-slate-100 dark:border-slate-800">
            <Building2 className="w-5 h-5 text-emerald-600" />
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">Related Public News & Sentiment</h3>
          </div>
          <div className="space-y-3">
            {newsList.map((n) => (
              <div key={n.id} className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-100 dark:border-slate-800">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <a href={n.url} target="_blank" rel="noreferrer" className="text-xs font-semibold text-slate-900 dark:text-white hover:text-emerald-600 dark:hover:text-emerald-400">
                      {n.title}
                    </a>
                    <span className="block text-[11px] text-slate-400 mt-1">
                      {n.source} • {new Date(n.published_at).toLocaleDateString()}
                    </span>
                  </div>
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded shrink-0 ${
                    n.sentiment === 'Positive' ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300' : (n.sentiment === 'Negative' ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300' : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300')
                  }`}>
                    {n.sentiment}
                  </span>
                </div>
                {n.summary && <p className="text-xs text-slate-600 dark:text-slate-400 mt-2">{n.summary}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
