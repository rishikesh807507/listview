import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, ShieldCheck, AlertCircle, BarChart2, 
  HelpCircle, RefreshCw, Layers 
} from 'lucide-react';
import { fetchBatchPredictions, fetchStockPrediction } from '../api/client';
import { SearchableStockSelector } from '../components/SearchableStockSelector';

export const Predictions: React.FC = () => {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedStock, setSelectedStock] = useState<string>('RELIANCE');
  const [selectedModel, setSelectedModel] = useState<string>('RandomForest');
  const [singlePred, setSinglePred] = useState<any>(null);
  const [singleLoading, setSingleLoading] = useState<boolean>(false);
  const [singleError, setSingleError] = useState<string | null>(null);

  useEffect(() => {
    const loadBatch = async () => {
      setLoading(true);
      try {
        const res = await fetchBatchPredictions();
        setPredictions(res.predictions || []);
      } catch (err) {
        console.error("Error loading batch predictions", err);
      } finally {
        setLoading(false);
      }
    };
    loadBatch();
  }, []);

  const loadSinglePrediction = async (sym: string, model: string) => {
    if (!sym) return;
    setSelectedStock(sym);
    setSelectedModel(model);
    setSingleLoading(true);
    setSingleError(null);
    setSinglePred(null);
    try {
      const res = await fetchStockPrediction(sym, model);
      setSinglePred(res);
      setSingleError(null);
    } catch (err: any) {
      console.error("Error loading single prediction", err);
      const msg = err?.response?.data?.detail || "Historical data unavailable for this stock (insufficient stored daily candles to train ML model).";
      setSingleError(msg);
      setSinglePred(null);
    } finally {
      setSingleLoading(false);
    }
  };

  useEffect(() => {
    loadSinglePrediction(selectedStock, selectedModel);
  }, []);

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">AI Stock Direction & Volatility Engine</h1>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Purely open-source machine learning (Scikit-Learn, XGBoost). Walk-forward time-series validation with zero lookahead bias.
            </p>
          </div>

          <div className="px-3 py-1.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-lg text-xs font-semibold text-emerald-800 dark:text-emerald-300">
            Strict Ethical AI: No "Buy Now" • Probabilities Only
          </div>
        </div>
      </div>

      {/* Interactive Single-Stock Forecaster */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 gap-3">
          <h2 className="font-bold text-sm text-slate-900 dark:text-white">Custom Time-Series Forecast Inspector</h2>

          {/* Model and Stock Selectors */}
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 w-full sm:w-auto">
            <div className="w-full sm:w-64">
              <SearchableStockSelector
                value={selectedStock}
                onChange={(sym) => loadSinglePrediction(sym, selectedModel)}
                placeholder="Search stock to forecast..."
                allowClear={false}
              />
            </div>

            <select
              value={selectedModel}
              onChange={(e) => loadSinglePrediction(selectedStock, e.target.value)}
              className="text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-2 font-semibold text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500 shrink-0"
            >
              <option value="RandomForest">Random Forest (Ensemble)</option>
              <option value="XGBoost">XGBoost (Gradient Boosted)</option>
            </select>
          </div>
        </div>

        {singleLoading ? (
          <div className="flex items-center justify-center p-8">
            <div className="w-6 h-6 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : singlePred ? (
          <div className="mt-4 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Direction Probability</span>
                <div className="text-xl font-extrabold text-slate-900 dark:text-white mt-1">
                  {singlePred.positive_prob}% Upside
                </div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400">{singlePred.target_timeframe}</span>
              </div>

              <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Expected Return Range</span>
                <div className="text-xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">
                  {singlePred.expected_return_min}% to +{singlePred.expected_return_max}%
                </div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400">Median Est: {singlePred.expected_return_mid}%</span>
              </div>

              <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Confidence & Volatility</span>
                <div className="text-sm font-bold text-slate-800 dark:text-slate-200 mt-1">
                  <span className="px-2 py-0.5 rounded text-xs bg-emerald-100 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300">{singlePred.confidence}</span>
                </div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400">20D Volatility: {singlePred.volatility_annualized}% p.a.</span>
              </div>

              <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Validation Accuracy</span>
                <div className="text-xl font-extrabold text-slate-900 dark:text-white mt-1">
                  {singlePred.metrics?.walk_forward_accuracy}
                </div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400">MAE: {singlePred.metrics?.mae} • F1: {singlePred.metrics?.f1_score}</span>
              </div>
            </div>

            {/* Model Transparency Audit */}
            <div className="bg-slate-50 dark:bg-slate-800/40 rounded-lg p-4 border border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300 space-y-2">
              <h4 className="font-bold text-slate-900 dark:text-white text-xs uppercase tracking-wider">Model Transparency & Audit Trail</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-[11px]">
                <div><strong>Validation Method:</strong> {singlePred.validation_method}</div>
                <div><strong>Training Window:</strong> {singlePred.training_period}</div>
                <div><strong>Splits Tested:</strong> {singlePred.metrics?.splits_tested} Walk-Forward Folds</div>
              </div>
              <div className="text-[11px] pt-1">
                <strong>Features Used:</strong> {singlePred.features_used?.join(', ')}
              </div>
            </div>
          </div>
        ) : singleError ? (
          <div className="mt-4 p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-lg text-xs text-amber-800 dark:text-amber-300 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-amber-600 dark:text-amber-400" />
            <div>
              <span className="font-bold">Historical data unavailable:</span> {singleError}
            </div>
          </div>
        ) : null}
      </div>

      {/* Batch Overview Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Tracked Large-Cap AI Direction Forecasts</span>
          <span className="text-[11px] text-slate-400">Strict walk-forward scoring</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-slate-100 dark:border-slate-800">
              <tr>
                <th className="py-3 px-4">Symbol</th>
                <th className="py-3 px-4 text-right">Current Price</th>
                <th className="py-3 px-4 text-right">Positive Direction Prob</th>
                <th className="py-3 px-4 text-right">Return Range (1-5D)</th>
                <th className="py-3 px-4 text-center">Confidence</th>
                <th className="py-3 px-4 text-center">Walk-Forward Acc</th>
                <th className="py-3 px-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {predictions.map((p) => (
                <tr key={p.symbol} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40">
                  <td className="py-3 px-4 font-bold text-slate-900 dark:text-white">
                    <Link to={`/stocks/${p.symbol}`} className="hover:text-emerald-600 dark:hover:text-emerald-400">
                      {p.symbol}
                    </Link>
                    <span className="block text-[11px] text-slate-400 font-normal">{p.name}</span>
                  </td>
                  <td className="py-3 px-4 text-right font-semibold text-slate-900 dark:text-white">
                    {p.current_price && p.current_price > 0 ? `₹${Number(p.current_price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '—'}
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-slate-900 dark:text-white">
                    {p.positive_prob}%
                  </td>
                  <td className="py-3 px-4 text-right text-emerald-600 dark:text-emerald-400 font-semibold">
                    {p.expected_return_range}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      p.confidence === 'High' ? 'bg-emerald-100 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300' : 'bg-amber-100 dark:bg-amber-950/50 text-amber-800 dark:text-amber-300'
                    }`}>
                      {p.confidence}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center font-medium text-slate-700 dark:text-slate-300">
                    {p.walk_forward_accuracy}
                  </td>
                  <td className="py-3 px-4">
                    <button
                      onClick={() => loadSinglePrediction(p.symbol, selectedModel)}
                      className="text-xs text-emerald-600 dark:text-emerald-400 hover:text-emerald-800 dark:hover:text-emerald-300 font-semibold underline"
                    >
                      Inspect Audit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
