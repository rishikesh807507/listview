import React, { useState, useEffect, useRef } from 'react';
import { Search, X, ChevronDown, Check, Building2, AlertCircle } from 'lucide-react';
import { searchStocks } from '../api/client';

export interface StockOption {
  symbol: string;
  name: string;
  company_name?: string;
  exchange?: string;
  isin?: string;
  sector?: string;
  instrument_type?: string;
  current_price?: number;
  change?: number;
  change_percent?: number;
}

interface SearchableStockSelectorProps {
  value: string;
  onChange: (symbol: string, stock?: StockOption) => void;
  placeholder?: string;
  className?: string;
  label?: string;
  allowClear?: boolean;
}

export const SearchableStockSelector: React.FC<SearchableStockSelectorProps> = ({
  value,
  onChange,
  placeholder = "Search stock by symbol or company name...",
  className = "",
  label,
  allowClear = true,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<StockOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [highlightIndex, setHighlightIndex] = useState(0);
  const [selectedStock, setSelectedStock] = useState<StockOption | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Initial lookup if value is set externally
  useEffect(() => {
    if (value && (!selectedStock || selectedStock.symbol.toUpperCase() !== value.toUpperCase())) {
      searchStocks(value)
        .then((res) => {
          if (Array.isArray(res) && res.length > 0) {
            const match = res.find((s: any) => s.symbol.toUpperCase() === value.toUpperCase()) || res[0];
            setSelectedStock({
              symbol: match.symbol,
              name: match.name || match.company_name,
              company_name: match.company_name || match.name,
              exchange: match.exchange || 'NSE',
              sector: match.sector,
              current_price: match.current_price,
            });
          }
        })
        .catch(() => {});
    } else if (!value) {
      setSelectedStock(null);
    }
  }, [value]);

  // Debounced search API request
  useEffect(() => {
    if (!isOpen) return;

    setLoading(true);
    setError(null);

    const timer = setTimeout(async () => {
      try {
        const q = query.trim();
        const data = await searchStocks(q);
        if (Array.isArray(data)) {
          const normalized: StockOption[] = data.map((item: any) => ({
            symbol: item.symbol,
            name: item.company_name || item.name,
            company_name: item.company_name || item.name,
            exchange: item.exchange || 'NSE',
            isin: item.isin,
            sector: item.sector,
            instrument_type: item.instrument_type || 'EQUITY',
            current_price: item.current_price,
            change: item.change,
            change_percent: item.change_percent,
          }));
          setResults(normalized);
          setHighlightIndex(0);
        } else {
          setResults([]);
        }
      } catch (err) {
        console.error("Stock search API error:", err);
        setError("Unable to search stocks. Try again.");
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query, isOpen]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
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

  const handleSelect = (stock: StockOption) => {
    setSelectedStock(stock);
    onChange(stock.symbol, stock);
    setIsOpen(false);
    setQuery('');
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedStock(null);
    onChange('', undefined);
    setQuery('');
    setResults([]);
    inputRef.current?.focus();
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

  // Helper to highlight matching text in ticker/name
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
    <div className={`relative ${className}`} ref={containerRef}>
      {label && (
        <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1">
          {label}
        </label>
      )}

      {/* Selector Trigger Input */}
      <div
        onClick={() => {
          setIsOpen(true);
          inputRef.current?.focus();
        }}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg text-xs cursor-pointer hover:border-emerald-500/50 focus-within:border-emerald-500 focus-within:ring-1 focus-within:ring-emerald-500 transition-all shadow-xs"
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <Search className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          {isOpen ? (
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={selectedStock ? `${selectedStock.name || selectedStock.company_name} (${selectedStock.symbol})` : placeholder}
              className="w-full bg-transparent border-none outline-hidden text-xs text-slate-900 dark:text-slate-100 placeholder:text-slate-400 p-0"
              autoFocus
            />
          ) : selectedStock ? (
            <div className="flex items-center gap-2 truncate">
              <span className="font-bold text-slate-900 dark:text-white shrink-0">{selectedStock.symbol}</span>
              <span className="text-slate-500 dark:text-slate-400 truncate text-[11px]">
                {selectedStock.name || selectedStock.company_name}
              </span>
              {selectedStock.exchange && (
                <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 shrink-0">
                  {selectedStock.exchange}
                </span>
              )}
            </div>
          ) : value ? (
            <span className="font-bold text-slate-900 dark:text-white">{value}</span>
          ) : (
            <span className="text-slate-400 dark:text-slate-500">{placeholder}</span>
          )}
        </div>

        <div className="flex items-center gap-1 shrink-0">
          {allowClear && (selectedStock || value) && (
            <button
              type="button"
              onClick={handleClear}
              className="p-0.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
              title="Clear selection"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </div>
      </div>

      {/* Autocomplete Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-50 left-0 right-0 mt-1 max-h-72 overflow-hidden bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl flex flex-col">
          {/* Header with Result Count */}
          {!loading && !error && results.length > 0 && (
            <div className="px-3 py-1.5 bg-slate-50 dark:bg-slate-800/80 border-b border-slate-100 dark:border-slate-800 text-[10px] font-medium text-slate-500 dark:text-slate-400 flex justify-between items-center shrink-0">
              <span>{results.length} {results.length === 1 ? 'stock found' : 'stocks found'}</span>
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
                {query.trim() ? `No stocks found for '${query.trim()}'` : "Type a company name or ticker to search"}
              </div>
            ) : (
              results.map((stock, idx) => {
                const isSelected = (value || selectedStock?.symbol)?.toUpperCase() === stock.symbol.toUpperCase();
                const isHighlighted = idx === highlightIndex;

                return (
                  <div
                    key={stock.symbol}
                    onClick={() => handleSelect(stock)}
                    onMouseEnter={() => setHighlightIndex(idx)}
                    className={`flex items-center justify-between px-3 py-2.5 cursor-pointer text-xs transition-colors ${
                      isHighlighted
                        ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200'
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/60 text-slate-800 dark:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-7 h-7 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0">
                        <Building2 className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
                      </div>
                      <div className="truncate">
                        {/* Company Name on Top */}
                        <div className="font-semibold text-slate-900 dark:text-white truncate text-[12px]">
                          {highlightMatch(stock.name || stock.company_name, query)}
                        </div>
                        {/* SYMBOL • EXCHANGE below */}
                        <div className="flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                          <span className="font-mono font-bold text-slate-700 dark:text-slate-300">
                            {highlightMatch(stock.symbol, query)}
                          </span>
                          <span>•</span>
                          <span className="px-1 py-0.2 rounded text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                            {stock.exchange || 'NSE'}
                          </span>
                          {stock.sector && (
                            <>
                              <span>•</span>
                              <span className="truncate">{stock.sector}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0 ml-3">
                      {stock.current_price !== undefined && stock.current_price !== null && stock.current_price > 0 && (
                        <div className="text-right">
                          <span className="font-semibold text-slate-900 dark:text-white block">
                            ₹{stock.current_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </span>
                          {stock.change_percent !== undefined && stock.change_percent !== null && (
                            <span className={`text-[10px] font-medium ${stock.change_percent >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                              {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                            </span>
                          )}
                        </div>
                      )}
                      {isSelected && <Check className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />}
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

export default SearchableStockSelector;
