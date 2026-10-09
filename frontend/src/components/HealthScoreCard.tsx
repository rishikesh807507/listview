import React from 'react';
import { ShieldCheck, AlertCircle, CheckCircle2, TrendingUp } from 'lucide-react';

interface ComponentDetail {
  status: string;
  score: number;
  detail: string;
}

interface HealthScoreCardProps {
  score: number;
  overallHealth: string;
  components: Record<string, ComponentDetail>;
  disclaimer: string;
}

export const HealthScoreCard: React.FC<HealthScoreCardProps> = ({
  score,
  overallHealth,
  components,
  disclaimer
}) => {
  let badgeColor = "bg-emerald-100 text-emerald-800 border-emerald-300";
  if (overallHealth === "Moderate") badgeColor = "bg-amber-100 text-amber-800 border-amber-300";
  if (overallHealth === "Watchlist" || overallHealth === "Weak") badgeColor = "bg-rose-100 text-rose-800 border-rose-300";

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h3 className="font-semibold text-slate-800 dark:text-white text-base">Fundamental Health Score</h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Objective 10-pillar mathematical appraisal from public filings</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="text-2xl font-bold text-slate-900 dark:text-white">{score}</span>
            <span className="text-xs text-slate-400 font-medium"> / 100</span>
          </div>
          <span className={`px-2.5 py-1 text-xs font-semibold rounded-md border ${badgeColor}`}>
            {overallHealth}
          </span>
        </div>
      </div>

      {/* Grid of 10 components */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {Object.entries(components).map(([name, data]) => {
          const isGood = data.score >= 7;
          const isNeutral = data.score >= 4 && data.score < 7;
          
          return (
            <div key={name} className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-100 dark:border-slate-800 flex flex-col justify-between">
              <div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium block truncate" title={name}>{name}</span>
                <span className="text-xs font-semibold text-slate-900 dark:text-white mt-0.5 block">{data.detail}</span>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${
                  isGood ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300' : (isNeutral ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300' : 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300')
                }`}>
                  {data.status}
                </span>
                <span className="text-[10px] text-slate-400">{data.score}/10</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-start gap-1.5 text-[11px] text-slate-400">
        <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
        <span>{disclaimer}</span>
      </div>
    </div>
  );
};
