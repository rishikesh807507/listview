import React, { useState } from 'react';
import { Settings as SettingsIcon, Database, Upload, ShieldCheck, CheckCircle2, AlertCircle, Sun, Moon, Monitor } from 'lucide-react';
import axios from 'axios';
import { useTheme } from '../context/ThemeContext';

export const SettingsPage: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const [ipoFile, setIpoFile] = useState<File | null>(null);
  const [fundFile, setFundFile] = useState<File | null>(null);
  const [ipoStatus, setIpoStatus] = useState<string>('');
  const [fundStatus, setFundStatus] = useState<string>('');

  const handleUploadIPO = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ipoFile) return;
    const formData = new FormData();
    formData.append('file', ipoFile);
    try {
      const res = await axios.post('/api/ipos/import-csv', formData);
      setIpoStatus(res.data.message || 'Import successful!');
    } catch (err: any) {
      setIpoStatus('Error uploading IPO file: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleUploadFund = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fundFile) return;
    const formData = new FormData();
    formData.append('file', fundFile);
    try {
      const res = await axios.post('/api/fundamentals/import-csv', formData);
      setFundStatus(res.data.message || 'Import successful!');
    } catch (err: any) {
      setFundStatus('Error uploading fundamentals: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs">
        <div className="flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
          <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">System Settings & Data Architecture</h1>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Appearance preferences, transparency controls, offline demo datasets, manual data injection, and self-hosted architectural guarantees.
        </p>
      </div>

      {/* Theme Preference */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-800">
          <Sun className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          <h3 className="font-bold text-sm text-slate-900 dark:text-white">Appearance & Theme</h3>
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-400">
          Select your visual appearance preference. Saved locally across browser sessions.
        </p>
        <div className="grid grid-cols-3 gap-3 max-w-md">
          <button
            onClick={() => setTheme('light')}
            className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg border text-xs font-semibold transition-all ${
              theme === 'light'
                ? 'border-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 ring-2 ring-emerald-500/20'
                : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-300'
            }`}
          >
            <Sun className="w-4 h-4" />
            <span>Light</span>
          </button>
          <button
            onClick={() => setTheme('dark')}
            className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg border text-xs font-semibold transition-all ${
              theme === 'dark'
                ? 'border-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 ring-2 ring-emerald-500/20'
                : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-300'
            }`}
          >
            <Moon className="w-4 h-4" />
            <span>Dark</span>
          </button>
          <button
            onClick={() => setTheme('system')}
            className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg border text-xs font-semibold transition-all ${
              theme === 'system'
                ? 'border-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 ring-2 ring-emerald-500/20'
                : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-300'
            }`}
          >
            <Monitor className="w-4 h-4" />
            <span>System</span>
          </button>
        </div>
      </div>

      {/* Free Data Fallback Cascade Visual */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-800">
          <ShieldCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          <h3 className="font-bold text-sm text-slate-900 dark:text-white">Zero-Cost Fallback Cascade</h3>
        </div>

        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          The platform operates strictly on the <strong>Free Forever Principle</strong>. It contains ₹0 external subscriptions, ₹0 API-key dependencies, and zero cloud lock-in. External providers are decoupled via an abstraction layer with guaranteed 4-tier fallbacks:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 bg-emerald-50 dark:bg-emerald-950/30 rounded-lg border border-emerald-200 dark:border-emerald-800">
            <span className="text-[10px] font-bold text-emerald-800 dark:text-emerald-300 uppercase block">Tier 1: Community APIs</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200 block mt-1">0xramm Indian Stock API</span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">Live quotes when available</span>
          </div>

          <div className="p-3 bg-emerald-50 dark:bg-emerald-950/30 rounded-lg border border-emerald-200 dark:border-emerald-800">
            <span className="text-[10px] font-bold text-emerald-800 dark:text-emerald-300 uppercase block">Tier 2: Public Open Data</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200 block mt-1">Spectrumz00 GMP Data</span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">Open-source CC BY 4.0 data</span>
          </div>

          <div className="p-3 bg-amber-50 dark:bg-amber-950/30 rounded-lg border border-amber-200 dark:border-amber-800">
            <span className="text-[10px] font-bold text-amber-800 dark:text-amber-300 uppercase block">Tier 3: Local Database Cache</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200 block mt-1">SQLite / PostgreSQL</span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">Self-accumulated history</span>
          </div>

          <div className="p-3 bg-blue-50 dark:bg-blue-950/30 rounded-lg border border-blue-200 dark:border-blue-800">
            <span className="text-[10px] font-bold text-blue-800 dark:text-blue-300 uppercase block">Tier 4: Offline Demo Mode</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200 block mt-1">Bundled CSV / JSON</span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">Runs completely offline</span>
          </div>
        </div>

        <div className="text-[11px] text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/60 p-3 rounded border border-slate-100 dark:border-slate-800 italic">
          "Core application is self-hosted and uses open-source/free data sources where available. External data providers may change availability or terms."
        </div>
      </div>

      {/* Manual CSV/JSON Import Interface */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* IPO Data Import */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-800">
            <Upload className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">Import IPO Data (CSV)</h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Allows academic, college, or offline evaluations to load new public issues directly via CSV files.
          </p>

          <form onSubmit={handleUploadIPO} className="space-y-3">
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setIpoFile(e.target.files?.[0] || null)}
              className="text-xs text-slate-600 dark:text-slate-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 dark:file:bg-emerald-950/60 file:text-emerald-700 dark:file:text-emerald-300 hover:file:bg-emerald-100 cursor-pointer"
            />
            <div>
              <button
                type="submit"
                disabled={!ipoFile}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold"
              >
                Upload & Ingest IPOs
              </button>
            </div>
            {ipoStatus && (
              <span className="text-xs text-emerald-700 dark:text-emerald-400 font-semibold block">{ipoStatus}</span>
            )}
          </form>
        </div>

        {/* Fundamentals Import */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-800">
            <Upload className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">Import Fundamentals (CSV)</h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Upload custom balance sheet, income statement, and valuation metrics without third-party fees.
          </p>

          <form onSubmit={handleUploadFund} className="space-y-3">
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setFundFile(e.target.files?.[0] || null)}
              className="text-xs text-slate-600 dark:text-slate-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 dark:file:bg-emerald-950/60 file:text-emerald-700 dark:file:text-emerald-300 hover:file:bg-emerald-100 cursor-pointer"
            />
            <div>
              <button
                type="submit"
                disabled={!fundFile}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold"
              >
                Upload & Ingest Fundamentals
              </button>
            </div>
            {fundStatus && (
              <span className="text-xs text-emerald-700 dark:text-emerald-400 font-semibold block">{fundStatus}</span>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

