import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  TrendingUp, Search, Moon, Sun, Laptop, Menu, X, 
  Layers, PieChart, ShieldAlert, BarChart2, Briefcase, 
  PlayCircle, Sliders, Filter, Newspaper, Bookmark,
  ShieldCheck, RefreshCw, Sparkles, Settings as SettingsIcon
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { SearchableStockSelector } from './SearchableStockSelector';

export const Navbar: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [themeDropdownOpen, setThemeDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, setTheme, isDark } = useTheme();

  const navLinks = [
    { path: '/', label: 'Dashboard', icon: BarChart2 },
    { path: '/markets', label: 'Markets', icon: TrendingUp },
    { path: '/stocks', label: 'Stocks', icon: Layers },
    { path: '/ipos', label: 'IPO Center', icon: PieChart },
    { path: '/gmp', label: 'GMP Tracker', icon: ShieldAlert },
    { path: '/predictions', label: 'AI Predict', icon: Sparkles },
    { path: '/screener', label: 'Screener', icon: Filter },
    { path: '/compare', label: 'Compare', icon: Sliders },
    { path: '/portfolio', label: 'Portfolio', icon: Briefcase },
    { path: '/backtest', label: 'Backtest', icon: PlayCircle },
    { path: '/sectors', label: 'Sectors', icon: Layers },
    { path: '/news', label: 'News', icon: Newspaper },
    { path: '/watchlist', label: 'Watchlist', icon: Bookmark },
    { path: '/data-health', label: 'Data Health', icon: ShieldCheck },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-xs group-hover:bg-emerald-700 transition-colors">
                <TrendingUp className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-lg text-slate-900 dark:text-white tracking-tight">
                  List<span className="text-emerald-600 dark:text-emerald-400">view</span>
                </span>
                <span className="block text-[10px] text-slate-500 dark:text-slate-400 font-medium -mt-1">
                  Indian Stocks & IPO Intelligence
                </span>
              </div>
            </Link>
          </div>

          {/* Quick Search Autocomplete Bar */}
          <div className="hidden md:block w-72">
            <SearchableStockSelector
              value=""
              onChange={(sym) => {
                if (sym) {
                  navigate(`/stocks/${sym.toUpperCase()}`);
                }
              }}
              placeholder="Search ticker (e.g. RELIANCE, TCS)..."
            />
          </div>

          {/* Controls: Theme Toggle, Settings & Mobile Menu */}
          <div className="flex items-center gap-1.5">
            {/* Theme Toggle Dropdown */}
            <div className="relative">
              <button
                onClick={() => setThemeDropdownOpen(!themeDropdownOpen)}
                className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-950 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                title={`Theme: ${theme}`}
                aria-label="Toggle theme"
              >
                {theme === 'dark' ? (
                  <Moon className="w-4 h-4 text-emerald-400" />
                ) : theme === 'light' ? (
                  <Sun className="w-4 h-4 text-amber-500" />
                ) : (
                  <Laptop className="w-4 h-4 text-slate-400" />
                )}
              </button>

              {themeDropdownOpen && (
                <div 
                  className="absolute right-0 mt-2 w-32 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-1 z-50 text-xs"
                  onClick={() => setThemeDropdownOpen(false)}
                >
                  <button
                    onClick={() => setTheme('light')}
                    className={`w-full flex items-center gap-2 px-3 py-1.5 text-left transition-colors ${
                      theme === 'light' 
                        ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 font-bold' 
                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50'
                    }`}
                  >
                    <Sun className="w-3.5 h-3.5 text-amber-500" />
                    <span>Light</span>
                  </button>
                  <button
                    onClick={() => setTheme('dark')}
                    className={`w-full flex items-center gap-2 px-3 py-1.5 text-left transition-colors ${
                      theme === 'dark' 
                        ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-400 font-bold' 
                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50'
                    }`}
                  >
                    <Moon className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Dark</span>
                  </button>
                  <button
                    onClick={() => setTheme('system')}
                    className={`w-full flex items-center gap-2 px-3 py-1.5 text-left transition-colors ${
                      theme === 'system' 
                        ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-500 font-bold' 
                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50'
                    }`}
                  >
                    <Laptop className="w-3.5 h-3.5 text-slate-400" />
                    <span>System</span>
                  </button>
                </div>
              )}
            </div>

            {/* Transparency & Settings */}
            <Link
              to="/settings"
              className={`p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ${
                location.pathname === '/settings' ? 'bg-slate-100 dark:bg-slate-800 text-emerald-600 dark:text-emerald-400 font-semibold' : ''
              }`}
              title="Settings & Data Transparency"
            >
              <SettingsIcon className="w-4 h-4" />
            </Link>

            {/* Mobile Hamburger Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 md:hidden"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Secondary Navigation Row (Desktop) */}
        <div className="hidden md:flex items-center gap-1 overflow-x-auto py-2 border-t border-slate-100 dark:border-slate-800 no-scrollbar">
          {navLinks.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400 font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500'}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 pt-2 pb-4 space-y-2">
          <div className="mb-3">
            <SearchableStockSelector
              value=""
              onChange={(sym) => {
                if (sym) {
                  navigate(`/stocks/${sym.toUpperCase()}`);
                  setMobileMenuOpen(false);
                }
              }}
              placeholder="Search ticker (e.g. RELIANCE)..."
            />
          </div>
          {navLinks.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-emerald-50 dark:hover:bg-emerald-950/50 hover:text-emerald-700 dark:hover:text-emerald-400"
            >
              <item.icon className="w-4 h-4 text-slate-400 dark:text-slate-500" />
              <span>{item.label}</span>
            </Link>
          ))}
        </div>
      )}
    </header>
  );
};

export default Navbar;
