import React, { useState, useEffect, useRef } from 'react';
import { Search, X, ChevronDown, Check, PieChart, AlertCircle } from 'lucide-react';
import { searchIPOs } from '../api/client';

export interface IPOOption {
  id: number;
  company_name: string;
  symbol?: string;
  isin?: string;
  board?: string;
  exchange?: string;
  status: string;
  price_band?: string;
  issue_size_crore?: number;
  is_demo?: boolean;
}

interface SearchableIPOSelectorProps {
  selectorIndex: number;
  selectedIPO: IPOOption | null;
  onSelect: (ipo: IPOOption) => void;
  onRemove: () => void;
  canRemove: boolean;
  demoMode?: boolean;
}

export const SearchableIPOSelector: React.FC<SearchableIPOSelectorProps> = ({
  selectorIndex,
  selectedIPO,
  onSelect,
  onRemove,
  canRemove,
  demoMode = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<IPOOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [highlightIndex, setHighlightIndex] = useState(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    setLoading(true);
    setError(null);

    const timer = setTimeout(async () => {
      try {
        const q = query.trim() || 'A';
        const data = await searchIPOs(q, demoMode ? 'demo' : 'live');
        if (Array.isArray(data)) {
          const mapped: IPOOption[] = data.map((item: any) => ({
            id: item.id,
            company_name: item.company_name,
            symbol: item.symbol,
            isin: item.isin,
            board: item.board || item.ipo_type || 'Mainboard',
            exchange: item.exchange || 'NSE, BSE',
            status: item.status,
            price_band: item.price_band_high
              ? `₹${item.price_band_low || item.price_band_high} - ₹${item.price_band_high}`
              : (item.price_band || 'Not available'),
            issue_size_crore: item.issue_size_crore || item.issue_size,
            is_demo: item.is_demo,
          }));
          setResults(mapped);
          setHighlightIndex(0);
        } else {
          setResults([]);
        }
      } catch (err) {
        console.error("IPO search API error:", err);
        setError("Unable to search IPOs. Try again.");
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query, isOpen, demoMode]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Scroll active item into view
  useEffect(() => {
    if (isOpen && listRef.current) {
      const activeEl = listRef.current.children[highlightIndex] as HTMLElement;
      if (activeEl) {
        activeEl.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [highlightIndex, isOpen]);

  const handleSelect = (ipo: IPOOption) => {
    onSelect(ipo);
    setIsOpen(false);
    setQuery('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        setIsOpen(true);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightIndex((prev) => (prev < results.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightIndex((prev) => (prev > 0 ? prev - 1 : results.length - 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (results[highlightIndex]) {
        handleSelect(results[highlightIndex]);
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setIsOpen(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'OPEN':
        return 'bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800';
      case 'UPCOMING':
        return 'bg-blue-100 dark:bg-blue-950/80 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-800';
      case 'LISTED':
      case 'LISTING_TODAY':
        return 'bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-300 border-purple-300 dark:border-purple-800';
      case 'ALLOTMENT':
        return 'bg-indigo-100 dark:bg-indigo-950/80 text-indigo-800 dark:text-indigo-300 border-indigo-300 dark:border-indigo-800';
      default:
        return 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700';
    }
  };

  const highlightMatch = (text?: string, search?: string) => {
    if (!text) return null;
    if (!search || !search.trim()) return <span>{text}</span>;
    const cleanSearch = search.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${cleanSearch})`, 'gi');
    const parts = text.split(regex);
    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === search.trim().toLowerCase() ? (
            <span key={i} className="bg-emerald-100 dark:bg-emerald-950/80 text-emerald-900 dark:text-emerald-300 font-bold px-0.5 rounded-xs">
              {part}
            </span>
          ) : (
            part
          )
        )}
      </span>
    );
  };

  return (
    <div className="flex-1 min-w-[240px] relative" ref={containerRef}>
      <div className="flex items-center justify-between mb-1.5">
        <label className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
          <span className="w-4 h-4 rounded-full bg-slate-200 dark:bg-slate-800 text-[10px] flex items-center justify-center font-bold text-slate-700 dark:text-slate-300">
            {selectorIndex + 1}
          </span>
          <span>IPO {selectorIndex + 1}</span>
        </label>
        {canRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="text-[11px] text-rose-600 dark:text-rose-400 hover:underline inline-flex items-center gap-0.5"
            title="Remove selector"
          >
            <X className="w-3 h-3" />
            <span>Remove</span>
          </button>
        )}
      </div>

      {/* Trigger Box */}
      <div
        onClick={() => {
          setIsOpen(true);
          inputRef.current?.focus();
        }}
        className={`w-full p-2.5 bg-white dark:bg-slate-900 border rounded-xl text-xs cursor-pointer transition-all shadow-xs ${
          isOpen 
            ? 'border-emerald-500 ring-2 ring-emerald-500/20' 
            : selectedIPO 
            ? 'border-slate-300 dark:border-slate-700 hover:border-slate-400' 
            : 'border-dashed border-slate-300 dark:border-slate-700 hover:border-emerald-500'
        }`}
      >
        {isOpen ? (
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search company, symbol, ISIN..."
              className="w-full bg-transparent border-none outline-hidden text-xs text-slate-900 dark:text-slate-100 placeholder:text-slate-400 p-0"
              autoFocus
            />
          </div>
        ) : selectedIPO ? (
          <div className="space-y-1">
            <div className="flex items-center justify-between gap-1">
              <span className="font-bold text-slate-900 dark:text-white truncate">
                {selectedIPO.company_name}
              </span>
              <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold border uppercase shrink-0 ${getStatusBadge(selectedIPO.status)}`}>
                {selectedIPO.status}
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400 truncate">
              {selectedIPO.symbol && (
                <span className="font-mono font-semibold text-slate-700 dark:text-slate-300">
                  {selectedIPO.symbol}
                </span>
              )}
              <span>•</span>
              <span>{selectedIPO.exchange || 'NSE'}</span>
              <span>•</span>
              <span>{selectedIPO.board || 'Mainboard'}</span>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between text-slate-400 dark:text-slate-500 py-1">
            <div className="flex items-center gap-2">
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <span>Search IPO to compare...</span>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </div>
        )}
      </div>

      {/* Results Dropdown */}
      {isOpen && (
        <div className="absolute z-50 left-0 right-0 mt-1 max-h-72 overflow-hidden bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl flex flex-col">
          {/* Header */}
          {!loading && !error && results.length > 0 && (
            <div className="px-3 py-1.5 bg-slate-50 dark:bg-slate-800/80 border-b border-slate-100 dark:border-slate-800 text-[10px] font-medium text-slate-500 dark:text-slate-400 flex justify-between items-center shrink-0">
              <span>{results.length} {results.length === 1 ? 'IPO found' : 'IPOs found'}</span>
              <span className="text-[9px] text-slate-400">↑↓ to navigate • Enter to select</span>
            </div>
          )}

          <div ref={listRef} className="overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800/60 max-h-60">
            {loading ? (
              <div className="p-4 text-center text-xs text-slate-500 dark:text-slate-400 flex items-center justify-center gap-2">
                <div className="w-3.5 h-3.5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                <span>Searching...</span>
              </div>
            ) : error ? (
              <div className="p-4 text-center text-xs text-rose-500 dark:text-rose-400 flex items-center justify-center gap-1.5">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>{error}</span>
              </div>
            ) : results.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-500 dark:text-slate-400">
                {query.trim() ? `No IPOs found for '${query.trim()}'` : "Type a company, symbol, or ISIN"}
              </div>
            ) : (
              results.map((ipo, idx) => {
                const isSelected = selectedIPO?.id === ipo.id;
                const isHighlighted = idx === highlightIndex;

                return (
                  <div
                    key={ipo.id}
                    onClick={() => handleSelect(ipo)}
                    onMouseEnter={() => setHighlightIndex(idx)}
                    className={`p-2.5 cursor-pointer text-xs transition-colors ${
                      isHighlighted
                        ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-950 dark:text-emerald-200'
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/60 text-slate-800 dark:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="font-semibold text-slate-900 dark:text-white truncate text-[12px]">
                        {highlightMatch(ipo.company_name, query)}
                      </div>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold border uppercase shrink-0 ${getStatusBadge(ipo.status)}`}>
                        {ipo.status}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                      {ipo.symbol && (
                        <span className="font-mono font-bold text-slate-700 dark:text-slate-300">
                          {highlightMatch(ipo.symbol, query)}
                        </span>
                      )}
                      <span>•</span>
                      <span>{ipo.exchange || 'NSE'}</span>
                      <span>•</span>
                      <span>{ipo.board || 'Mainboard'}</span>
                      {isSelected && (
                        <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 ml-auto" />
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchableIPOSelector;
