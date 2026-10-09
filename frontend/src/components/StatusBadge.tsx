import React from 'react';
import { Wifi, Database, HardDrive, AlertTriangle } from 'lucide-react';

interface StatusBadgeProps {
  status?: string;
  source?: string;
  lastUpdated?: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status = "Cached",
  source = "Local Database",
  lastUpdated,
  className = ""
}) => {
  const isLive = status.toLowerCase().includes("live");
  const isCached = status.toLowerCase().includes("cached");
  const isDemo = status.toLowerCase().includes("demo");

  let badgeColor = "bg-amber-50 text-amber-700 border-amber-200";
  let Icon = Database;

  if (isLive) {
    badgeColor = "bg-emerald-50 text-emerald-700 border-emerald-200";
    Icon = Wifi;
  } else if (isDemo) {
    badgeColor = "bg-blue-50 text-blue-700 border-blue-200";
    Icon = HardDrive;
  } else if (!isCached) {
    badgeColor = "bg-rose-50 text-rose-700 border-rose-200";
    Icon = AlertTriangle;
  }

  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${badgeColor} ${className}`} title={`Source: ${source}${lastUpdated ? ` • Updated: ${lastUpdated}` : ''}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${isLive ? 'bg-emerald-500 animate-pulse' : (isCached ? 'bg-amber-500' : 'bg-blue-500')}`} />
      <Icon className="w-3.5 h-3.5" />
      <span>{status}</span>
      {source && <span className="opacity-70 text-[10px] hidden sm:inline">({source.split(' ')[0]})</span>}
    </div>
  );
};
