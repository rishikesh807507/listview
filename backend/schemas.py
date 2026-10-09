from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class StockBase(BaseModel):
    symbol: str
    name: str
    exchange: str = "NSE"
    isin: Optional[str] = None
    instrument_type: Optional[str] = "EQUITY"
    sector: Optional[str] = None
    industry: Optional[str] = None
    current_price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    dividend_yield: Optional[float] = None
    debt_to_equity: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    volume: Optional[float] = None

class StockResponse(StockBase):
    id: int
    is_active: bool
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PricePoint(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    class Config:
        from_attributes = True

class StockDetailResponse(BaseModel):
    stock: StockResponse
    status: str  # "Live", "Cached", "Demo"
    source: str
    last_updated: str
    disclaimer: str

class StockFundamentalsResponse(BaseModel):
    symbol: str
    revenue: float
    revenue_growth: float
    ebitda: float
    ebitda_margin: float
    net_profit: float
    profit_growth: float
    eps: float
    pe: float
    pb: float
    roe: float
    roce: float
    debt: float
    debt_to_equity: float
    current_ratio: float
    dividend_yield: float
    free_cash_flow: float
    promoter_holding: float
    market_cap: float
    enterprise_value: float
    period: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class HealthScoreResponse(BaseModel):
    symbol: str
    overall_health: str  # "Strong", "Moderate", "Watch", "Weak"
    score_out_of_100: float
    components: Dict[str, Dict[str, Any]]
    disclaimer: str

class IPOResponse(BaseModel):
    id: int
    symbol: Optional[str] = None
    company_name: str
    ipo_type: Optional[str] = None
    price_band_low: Optional[float] = None
    price_band_high: Optional[float] = None
    lot_size: Optional[int] = None
    issue_size: Optional[float] = None
    open_date: Optional[datetime] = None
    close_date: Optional[datetime] = None
    listing_date: Optional[datetime] = None
    face_value: Optional[float] = None
    fresh_issue: Optional[float] = None
    offer_for_sale: Optional[float] = None
    registrar: Optional[str] = None
    lead_managers: Optional[str] = None
    exchange: Optional[str] = None
    status: Optional[str] = None
    sector: Optional[str] = None
    revenue: Optional[float] = None
    profit: Optional[float] = None
    eps: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    debt: Optional[float] = None
    gmp: Optional[float] = None
    gmp_percent: Optional[float] = None
    estimated_listing_price: Optional[float] = None
    estimated_listing_gain: Optional[float] = None
    subscription_total: Optional[float] = None
    actual_listing_price: Optional[float] = None
    listing_day_close: Optional[float] = None
    listing_gain_percent: Optional[float] = None
    issue_price: Optional[float] = None

    class Config:
        from_attributes = True

class GMPResponse(BaseModel):
    id: int
    ipo_id: Optional[int] = None
    company_name: str
    gmp: float
    gmp_percent: float
    min_gmp: float
    max_gmp: float
    estimated_listing_price: float
    estimated_listing_gain: float
    source: str
    disclaimer: str
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    target_identifier: str
    target_type: str
    timeframe: str
    positive_prob: float
    expected_return_min: float
    expected_return_max: float
    confidence: str
    model_name: str
    features_used: List[str]
    metrics: Dict[str, Any]
    validation_method: str
    training_period: str
    created_at: datetime
    disclaimer: str

class NewsItem(BaseModel):
    id: int
    title: str
    source: str
    published_at: datetime
    url: Optional[str] = None
    related_stock: Optional[str] = None
    category: str
    sentiment: str
    sentiment_score: float
    summary: Optional[str] = None

    class Config:
        from_attributes = True

class MarketOverviewResponse(BaseModel):
    indices: List[Dict[str, Any]]
    top_gainers: List[Dict[str, Any]]
    top_losers: List[Dict[str, Any]]
    most_active: List[Dict[str, Any]]
    market_stats: Dict[str, Any]
    data_status: str
    source: str
    updated_at: str

class PortfolioItemCreate(BaseModel):
    symbol: str
    quantity: int
    buy_price: float
    notes: Optional[str] = None

class PortfolioItemResponse(BaseModel):
    id: int
    symbol: str
    quantity: int
    buy_price: float
    buy_date: datetime
    notes: Optional[str] = None
    current_price: float = 0.0
    current_value: float = 0.0
    invested_value: float = 0.0
    profit_loss: float = 0.0
    return_percent: float = 0.0
    sector: Optional[str] = None

class BacktestRequest(BaseModel):
    symbol: str
    strategy: str  # "SMA", "EMA", "RSI", "MACD", "Momentum"
    initial_capital: float = 100000.0
    parameters: Optional[Dict[str, Any]] = None

class BacktestResponse(BaseModel):
    symbol: str
    strategy: str
    initial_capital: float
    final_capital: float
    return_percent: float
    benchmark_return: float
    max_drawdown: float
    total_trades: int
    winning_trades: int
    win_rate: float
    trades: List[Dict[str, Any]]
    equity_curve: List[Dict[str, Any]]
    label: str = "Historical Simulation Only"
