import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, CandlestickSeries, LineSeries, AreaSeries, HistogramSeries, type IChartApi } from 'lightweight-charts';
import { useTheme } from '../context/ThemeContext';
import { AlertCircle } from 'lucide-react';

export interface CandleData {
  time: string | number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TradingViewChartProps {
  candles: CandleData[];
  symbol: string;
  onTimeframeChange?: (tf: string) => void;
  selectedTimeframe?: string;
}

export const TradingViewChart: React.FC<TradingViewChartProps> = ({
  candles,
  symbol,
  onTimeframeChange,
  selectedTimeframe = '1Y'
}) => {
  const { isDark } = useTheme();
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [chartType, setChartType] = useState<'candlestick' | 'line' | 'area'>('candlestick');
  const [showSMA, setShowSMA] = useState<boolean>(true);
  const [showEMA, setShowEMA] = useState<boolean>(true);

  const timeframes = ['1D', '1W', '1M', '3M', '6M', '1Y', '3Y', '5Y', 'MAX'];

  useEffect(() => {
    // Clean up previous chart instance
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    if (!chartContainerRef.current || candles.length === 0) return;

    const container = chartContainerRef.current;
    const chart = createChart(container, {
      layout: {
        background: { type: ColorType.Solid, color: isDark ? '#0f172a' : '#ffffff' },
        textColor: isDark ? '#94a3b8' : '#334155',
        fontFamily: 'Inter, sans-serif',
      },
      grid: {
        vertLines: { color: isDark ? '#1e293b' : '#f1f5f9' },
        horzLines: { color: isDark ? '#1e293b' : '#f1f5f9' },
      },
      rightPriceScale: {
        borderColor: isDark ? '#334155' : '#e2e8f0',
        scaleMargins: {
          top: 0.1,
          bottom: 0.25,
        },
      },
      timeScale: {
        borderColor: isDark ? '#334155' : '#e2e8f0',
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        vertLine: { color: '#94a3b8', width: 1, style: 2 },
        horzLine: { color: '#94a3b8', width: 1, style: 2 },
      },
      width: container.clientWidth,
      height: 440,
    });

    chartRef.current = chart;

    // Filter, validate, deduplicate, and sort chronologically
    const seenTimes = new Set<string | number>();
    const sorted = [...candles]
      .filter((c) => {
        if (!c || c.time === undefined || c.time === null) return false;
        const o = Number(c.open);
        const h = Number(c.high);
        const l = Number(c.low);
        const cl = Number(c.close);
        if (isNaN(o) || isNaN(h) || isNaN(l) || isNaN(cl)) return false;
        if (o <= 0 || h <= 0 || l <= 0 || cl <= 0) return false;
        if (seenTimes.has(c.time)) return false;
        seenTimes.add(c.time);
        return true;
      })
      .sort((a, b) => (a.time > b.time ? 1 : a.time < b.time ? -1 : 0));

    if (sorted.length === 0) return;

    if (chartType === 'candlestick') {
      const mainSeries = chart.addSeries(CandlestickSeries, {
        upColor: '#10b981',
        downColor: '#ef4444',
        borderVisible: false,
        wickUpColor: '#10b981',
        wickDownColor: '#ef4444',
      });
      mainSeries.setData(sorted.map(c => ({
        time: c.time as any,
        open: c.open,
        high: Math.max(c.high, c.open, c.close),
        low: Math.min(c.low, c.open, c.close),
        close: c.close,
      })));
    } else if (chartType === 'line') {
      const lineSeries = chart.addSeries(LineSeries, {
        color: '#059669',
        lineWidth: 2,
      });
      lineSeries.setData(sorted.map(c => ({ time: c.time as any, value: c.close })));
    } else if (chartType === 'area') {
      const areaSeries = chart.addSeries(AreaSeries, {
        topColor: 'rgba(16, 185, 129, 0.4)',
        bottomColor: 'rgba(16, 185, 129, 0.01)',
        lineColor: '#10b981',
        lineWidth: 2,
      });
      areaSeries.setData(sorted.map(c => ({ time: c.time as any, value: c.close })));
    }

    // Volume histogram on bottom overlay
    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: '#cbd5e1',
      priceFormat: { type: 'volume' },
      priceScaleId: '', // separate scale
    });
    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });
    volumeSeries.setData(sorted.map(c => ({
      time: c.time as any,
      value: c.volume,
      color: c.close >= c.open ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)',
    })));

    // Optional 20-period SMA
    if (showSMA && sorted.length >= 20) {
      const smaData: { time: any; value: number }[] = [];
      for (let i = 19; i < sorted.length; i++) {
        let sum = 0;
        for (let j = 0; j < 20; j++) sum += sorted[i - j].close;
        smaData.push({ time: sorted[i].time as any, value: Number((sum / 20).toFixed(2)) });
      }
      const smaSeries = chart.addSeries(LineSeries, {
        color: '#3b82f6',
        lineWidth: 1,
        title: 'SMA 20',
      });
      smaSeries.setData(smaData);
    }

    // Optional 50-period EMA
    if (showEMA && sorted.length >= 50) {
      const emaData: { time: any; value: number }[] = [];
      const k = 2 / (50 + 1);
      let ema = sorted[0].close;
      for (let i = 0; i < sorted.length; i++) {
        ema = sorted[i].close * k + ema * (1 - k);
        if (i >= 49) {
          emaData.push({ time: sorted[i].time as any, value: Number(ema.toFixed(2)) });
        }
      }
      const emaSeries = chart.addSeries(LineSeries, {
        color: '#f59e0b',
        lineWidth: 1,
        title: 'EMA 50',
      });
      emaSeries.setData(emaData);
    }

    chart.timeScale().fitContent();

    // Resize handler
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [candles, chartType, showSMA, showEMA, isDark]);

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm p-4">
      {/* Controls Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3 pb-3 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
          <button
            onClick={() => setChartType('candlestick')}
            className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${
              chartType === 'candlestick' ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Candles
          </button>
          <button
            onClick={() => setChartType('line')}
            className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${
              chartType === 'line' ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Line
          </button>
          <button
            onClick={() => setChartType('area')}
            className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${
              chartType === 'area' ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Area
          </button>
        </div>

        {/* Indicators Toggle */}
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1 text-xs text-slate-600 dark:text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={showSMA}
              onChange={(e) => setShowSMA(e.target.checked)}
              className="rounded text-blue-600 focus:ring-blue-500"
            />
            <span className="font-medium text-blue-600 dark:text-blue-400">SMA 20</span>
          </label>
          <label className="flex items-center gap-1 text-xs text-slate-600 dark:text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={showEMA}
              onChange={(e) => setShowEMA(e.target.checked)}
              className="rounded text-amber-500 focus:ring-amber-400"
            />
            <span className="font-medium text-amber-600 dark:text-amber-400">EMA 50</span>
          </label>
        </div>

        {/* Timeframe buttons */}
        <div className="flex items-center gap-1 overflow-x-auto">
          {timeframes.map((tf) => (
            <button
              key={tf}
              onClick={() => onTimeframeChange && onTimeframeChange(tf)}
              className={`px-2.5 py-1 text-xs font-medium rounded-md transition-all ${
                selectedTimeframe === tf
                  ? 'bg-emerald-600 text-white font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Canvas or Fallback Message */}
      {candles.length === 0 ? (
        <div className="flex flex-col items-center justify-center w-full rounded-lg bg-slate-50 dark:bg-slate-800/40 text-slate-400 border border-dashed border-slate-200 dark:border-slate-800" style={{ height: '440px' }}>
          <AlertCircle className="w-8 h-8 text-slate-300 dark:text-slate-600 mb-2" />
          <span className="text-sm font-semibold text-slate-600 dark:text-slate-300">Historical data unavailable</span>
          <span className="text-xs text-slate-400 dark:text-slate-500 mt-1">No verified trading session records found for {symbol} ({selectedTimeframe}).</span>
        </div>
      ) : (
        <div ref={chartContainerRef} className="w-full relative" style={{ height: '440px' }} />
      )}

      {/* Footer Attribution */}
      <div className="mt-2 pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-400 dark:text-slate-500">
        <span>Displaying {candles.length} historical trading sessions for {symbol}</span>
        <span className="italic">Powered by TradingView Lightweight Charts (Apache-2.0 License)</span>
      </div>
    </div>
  );
};
