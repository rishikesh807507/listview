import axios from 'axios';

export const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
});

export interface StockItem {
  id: number;
  symbol: string;
  name: string;
  exchange: string;
  sector?: string;
  industry?: string;
  current_price?: number | null;
  change?: number | null;
  change_percent?: number | null;
  market_cap?: number | null;
  pe_ratio?: number | null;
  pb_ratio?: number | null;
  roe?: number | null;
  roce?: number | null;
  dividend_yield?: number | null;
  debt_to_equity?: number | null;
  high_52w?: number | null;
  low_52w?: number | null;
  volume?: number | null;
  updated_at?: string;
}

export interface IPOItem {
  id: number;
  symbol?: string;
  company_name: string;
  ipo_type: string;
  price_band_low: number;
  price_band_high: number;
  lot_size: number;
  issue_size: number;
  open_date: string;
  close_date: string;
  listing_date?: string;
  exchange: string;
  status: string;
  sector: string;
  revenue: number;
  profit: number;
  eps: number;
  roe: number;
  roce: number;
  debt: number;
  gmp?: number;
  gmp_percent?: number;
  estimated_listing_price?: number;
  estimated_listing_gain?: number;
  subscription_total?: number;
}

export interface GMPItem {
  id: number;
  ipo_id?: number;
  company_name: string;
  gmp: number;
  gmp_percent: number;
  min_gmp: number;
  max_gmp: number;
  estimated_listing_price: number;
  estimated_listing_gain: number;
  source: string;
  timestamp: string;
  disclaimer: string;
}

export const fetchMarketOverview = async () => (await api.get('/market/overview')).data;
export const fetchDataHealth = async () => (await api.get('/market/data-health')).data;
export const fetchStocks = async (params?: any) => (await api.get('/stocks', { params })).data;
export const fetchStockDetail = async (symbol: string) => (await api.get(`/stocks/${symbol}`)).data;
export const fetchStockHistory = async (symbol: string, timeframe: string = '1Y') => 
  (await api.get(`/stocks/${symbol}/history`, { params: { timeframe } })).data;
export const fetchStockHealth = async (symbol: string) => (await api.get(`/stocks/${symbol}/health`)).data;
export const fetchStockStatements = async (symbol: string) => (await api.get(`/fundamentals/${symbol}/statements`)).data;

export const fetchIPOs = async (params?: any) => (await api.get('/ipos', { params })).data;
export const fetchIPODetail = async (id: number | string) => (await api.get(`/ipos/${id}`)).data;
export const fetchIPOCalculator = async (id: number | string, investment_amount?: number, custom_price?: number) => 
  (await api.get(`/ipos/${id}/calculator`, { params: { investment_amount, custom_price } })).data;
export const toggleIPOWatchlist = async (id: number | string) => (await api.post(`/ipos/${id}/watchlist`)).data;
export const fetchIPODataHealth = async () => (await api.get('/ipos/data-health')).data;
export const refreshIPOs = async () => (await api.post('/ipos/refresh')).data;
export const fetchGMP = async (refresh: boolean = false) => (await api.get('/gmp', { params: { refresh } })).data;

export const fetchStockPrediction = async (symbol: string, model: string = 'RandomForest') => 
  (await api.get(`/predictions/stock/${symbol}`, { params: { model } })).data;
export const fetchIPOPrediction = async (id: number | string) => (await api.get(`/predictions/ipo/${id}`)).data;
export const fetchBatchPredictions = async () => (await api.get('/predictions/batch')).data;

export const fetchScreenerResults = async (params?: any) => (await api.get('/screener/run', { params })).data;
export const fetchSavedScreens = async () => (await api.get('/screener/saved')).data;

export const fetchSectors = async () => (await api.get('/sectors')).data;
export const fetchNews = async (params?: any) => (await api.get('/news', { params })).data;

export const fetchWatchlist = async () => (await api.get('/watchlist')).data;
export const addToWatchlist = async (symbol: string, notes?: string) => (await api.post('/watchlist', { symbol, notes })).data;
export const removeFromWatchlist = async (id: number) => (await api.delete(`/watchlist/${id}`)).data;

export const fetchPortfolio = async () => (await api.get('/portfolio')).data;
export const buyStock = async (data: { symbol: string; quantity: number; buy_price: number; notes?: string }) => 
  (await api.post('/portfolio/buy', data)).data;
export const sellStock = async (itemId: number, quantity: number) => 
  (await api.post(`/portfolio/sell/${itemId}`, null, { params: { quantity } })).data;

export const runBacktestSimulation = async (payload: { symbol: string; strategy: string; initial_capital: number; parameters?: any }) => 
  (await api.post('/backtest', payload)).data;

export const searchStocks = async (q: string) => (await api.get('/stocks/search', { params: { q } })).data;
export const searchIPOs = async (q: string, mode: string = 'live') => (await api.get('/ipos/search', { params: { q, mode } })).data;

export const compareStocks = async (symbols: string) => (await api.get('/compare/stocks', { params: { symbols } })).data;
export const compareIPOs = async (ids: string) => (await api.get('/ipos/compare', { params: { ids } })).data;

export const fetchAlerts = async () => (await api.get('/alerts')).data;
export const createAlert = async (data: { identifier: string; alert_type: string; condition: string; threshold: number }) => 
  (await api.post('/alerts', data)).data;
export const deleteAlert = async (id: number) => (await api.delete(`/alerts/${id}`)).data;
