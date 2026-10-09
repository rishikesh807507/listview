import React from 'react';
import { AlertCircle, Shield } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white dark:bg-slate-950 border-t border-slate-200 dark:border-slate-850 mt-16 text-slate-600 dark:text-slate-400 text-xs">
      {/* Statutory Financial Disclaimer Banner */}
      <div className="bg-amber-50/70 dark:bg-amber-950/30 border-b border-amber-200/60 dark:border-amber-900/40 py-3.5 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex items-start gap-3 text-amber-900 dark:text-amber-300 leading-relaxed text-xs">
          <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
          <p>
            <strong>MANDATORY FINANCIAL DISCLAIMER:</strong> This platform is for educational, academic, and informational purposes only. 
            Market data may be delayed, incomplete, inaccurate, or unavailable. AI predictions are purely statistical time-series estimates and are not guaranteed outcomes. 
            IPO GMP (Grey Market Premium) is unofficial, unregulated, and non-binding. Nothing on this platform constitutes financial, investment, or trading advice.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand & Principles */}
          <div className="md:col-span-2 space-y-3">
            <span className="font-bold text-base text-slate-900 dark:text-white tracking-tight">
              List<span className="text-emerald-600 dark:text-emerald-400">view</span> — Indian Stocks & IPO Intelligence
            </span>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-normal">
              A self-hosted Indian stock market and IPO intelligence platform. 
              Equipped with real time-series walk-forward ML direction modeling, 4-tier data fallback cascades, 
              and bundled offline datasets.
            </p>
            <div className="flex items-center gap-2 pt-1 text-[11px] text-emerald-700 dark:text-emerald-400 font-medium">
              <Shield className="w-3.5 h-3.5" />
              <span>Independent Analytics • Self-Hosted • Transparent Data Sourcing</span>
            </div>
          </div>

          {/* Open Data Sources & Attribution */}
          <div className="space-y-2">
            <h4 className="font-semibold text-slate-900 dark:text-white text-xs uppercase tracking-wider">Data Attribution</h4>
            <ul className="space-y-1.5 text-xs text-slate-500 dark:text-slate-400">
              <li>
                <a href="https://github.com/tradingview/lightweight-charts" target="_blank" rel="noreferrer" className="hover:text-emerald-600 dark:hover:text-emerald-400 underline">
                  TradingView Lightweight Charts
                </a> (Apache-2.0)
              </li>
              <li>
                <a href="https://github.com/Spectrumz00/india-ipo-gmp-data" target="_blank" rel="noreferrer" className="hover:text-emerald-600 dark:hover:text-emerald-400 underline">
                  india-ipo-gmp-data
                </a> (CC BY 4.0)
              </li>
              <li>
                <a href="https://github.com/0xramm/Indian-Stock-Market-API" target="_blank" rel="noreferrer" className="hover:text-emerald-600 dark:hover:text-emerald-400 underline">
                  Community Indian Stock API
                </a> (MIT)
              </li>
              <li>Public RSS Financial Feeds (ET, Mint, BS)</li>
            </ul>
          </div>

          {/* Architecture */}
          <div className="space-y-2">
            <h4 className="font-semibold text-slate-900 dark:text-white text-xs uppercase tracking-wider">Architecture</h4>
            <ul className="space-y-1.5 text-xs text-slate-500 dark:text-slate-400">
              <li>FastAPI + SQLAlchemy + Pydantic</li>
              <li>Scikit-Learn & XGBoost ML Pipeline</li>
              <li>React 19 + TypeScript + Vite + Tailwind CSS</li>
              <li>4-Tier Offline Fallback Engine</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 gap-2">
          <span>&copy; {new Date().getFullYear()} Listview. Open-source educational software.</span>
          <span>Core application is self-hosted and uses open-source/free data sources where available.</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
