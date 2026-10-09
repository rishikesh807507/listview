from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False, index=True)
    exchange = Column(String(20), default="NSE")
    isin = Column(String(50), nullable=True, index=True)
    instrument_type = Column(String(30), default="EQUITY")
    sector = Column(String(100), index=True)
    industry = Column(String(100))
    current_price = Column(Float, default=0.0)
    change = Column(Float, default=0.0)
    change_percent = Column(Float, default=0.0)
    market_cap = Column(Float, default=0.0)  # in Cr
    pe_ratio = Column(Float, default=0.0)
    pb_ratio = Column(Float, default=0.0)
    roe = Column(Float, default=0.0)
    roce = Column(Float, default=0.0)
    dividend_yield = Column(Float, default=0.0)
    debt_to_equity = Column(Float, default=0.0)
    high_52w = Column(Float, default=0.0)
    low_52w = Column(Float, default=0.0)
    volume = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prices = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    fundamentals = relationship("StockFundamentals", back_populates="stock", uselist=False, cascade="all, delete-orphan")


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), ForeignKey("stocks.symbol"), index=True, nullable=False)
    exchange = Column(String(20), default="NSE")
    timestamp = Column(DateTime, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    source = Column(String(50), default="local")
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("Stock", back_populates="prices")

    __table_args__ = (
        Index("idx_symbol_timestamp", "symbol", "timestamp"),
    )


class StockFundamentals(Base):
    __tablename__ = "stock_fundamentals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), ForeignKey("stocks.symbol"), unique=True, index=True, nullable=False)
    revenue = Column(Float, default=0.0)            # Cr
    revenue_growth = Column(Float, default=0.0)     # %
    ebitda = Column(Float, default=0.0)             # Cr
    ebitda_margin = Column(Float, default=0.0)      # %
    net_profit = Column(Float, default=0.0)         # Cr
    profit_growth = Column(Float, default=0.0)      # %
    eps = Column(Float, default=0.0)                # Rs
    pe = Column(Float, default=0.0)
    pb = Column(Float, default=0.0)
    roe = Column(Float, default=0.0)                # %
    roce = Column(Float, default=0.0)               # %
    debt = Column(Float, default=0.0)               # Cr
    debt_to_equity = Column(Float, default=0.0)
    current_ratio = Column(Float, default=0.0)
    dividend_yield = Column(Float, default=0.0)     # %
    free_cash_flow = Column(Float, default=0.0)     # Cr
    promoter_holding = Column(Float, default=0.0)   # %
    market_cap = Column(Float, default=0.0)         # Cr
    enterprise_value = Column(Float, default=0.0)   # Cr
    period = Column(String(20), default="FY2025-26")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stock = relationship("Stock", back_populates="fundamentals")


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    statement_type = Column(String(50), nullable=False)  # income, balance_sheet, cash_flow
    period_type = Column(String(20), default="annual")   # annual, quarterly
    year = Column(Integer, nullable=False)
    quarter = Column(String(10), nullable=True)          # Q1, Q2, Q3, Q4 or null
    data = Column(Text, nullable=False)                  # JSON string of all items
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_statement_lookup", "symbol", "statement_type", "year"),
    )


class IPO(Base):
    __tablename__ = "ipos"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(250), nullable=False, index=True)
    symbol = Column(String(50), index=True, nullable=True)
    isin = Column(String(50), nullable=True)
    exchange = Column(String(50), default="NSE, BSE")
    board = Column(String(50), default="Mainboard")       # Mainboard, SME
    ipo_type = Column(String(50), default="Mainboard")    # Legacy compatibility column
    issue_type = Column(String(100), default="Book Built Issue IPO")
    sector = Column(String(100), default="General")

    # Critical Timeline Dates
    issue_open_date = Column(DateTime, nullable=True)
    issue_close_date = Column(DateTime, nullable=True)
    allotment_date = Column(DateTime, nullable=True)
    refund_date = Column(DateTime, nullable=True)
    demat_credit_date = Column(DateTime, nullable=True)
    listing_date = Column(DateTime, nullable=True)

    # Pricing & Lot Details
    price_band_low = Column(Float, nullable=True)
    price_band_high = Column(Float, nullable=True)
    issue_price = Column(Float, nullable=True)
    lot_size = Column(Integer, nullable=True)
    minimum_application_amount = Column(Float, nullable=True)
    issue_size_crore = Column(Float, nullable=True)
    fresh_issue_crore = Column(Float, nullable=True)
    offer_for_sale_crore = Column(Float, nullable=True)
    face_value = Column(Float, default=10.0)

    # Reservation Quotas (%)
    qib_reservation = Column(Float, nullable=True)
    nii_reservation = Column(Float, nullable=True)
    retail_reservation = Column(Float, nullable=True)
    employee_reservation = Column(Float, nullable=True)

    # Intermediaries & Links
    registrar_name = Column(String(250), nullable=True)
    registrar_url = Column(String(500), nullable=True)
    lead_managers = Column(String(500), nullable=True)
    company_website = Column(String(500), nullable=True)
    nse_url = Column(String(500), nullable=True)
    bse_url = Column(String(500), nullable=True)
    sebi_url = Column(String(500), nullable=True)
    rhp_url = Column(String(500), nullable=True)
    prospectus_url = Column(String(500), nullable=True)

    # Status & Audit
    status = Column(String(50), default="UPCOMING", index=True) # UPCOMING, OPEN, CLOSED, ALLOTMENT, REFUND, DEMAT_CREDIT, LISTING_TODAY, LISTED, POSTPONED, WITHDRAWN, UNKNOWN
    source = Column(String(100), default="NSE Official Data")
    source_url = Column(String(500), nullable=True)
    source_updated_at = Column(DateTime, nullable=True)
    last_verified_at = Column(DateTime, default=datetime.utcnow)
    data_quality = Column(String(50), default="Verified")       # Verified, Needs Verification, Stale, Incomplete
    actual_listing_price = Column(Float, nullable=True)
    listing_day_close = Column(Float, nullable=True)
    listing_gain_percent = Column(Float, nullable=True)

    # Financial Fundamentals (if available from official RHP)
    revenue = Column(Float, nullable=True)                      # Cr
    profit = Column(Float, nullable=True)                       # Cr
    eps = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)
    roce = Column(Float, nullable=True)
    debt = Column(Float, nullable=True)

    # Strict Demo Isolation Flag
    is_demo = Column(Boolean, default=False, index=True)

    # Timestamps
    fetched_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    gmp = relationship("IPOGMP", back_populates="ipo", uselist=False, cascade="all, delete-orphan")
    subscription = relationship("IPOSubscription", back_populates="ipo", uselist=False, cascade="all, delete-orphan")
    subscription_history = relationship("IPOSubscriptionHistory", back_populates="ipo", cascade="all, delete-orphan")
    gmp_history = relationship("IPOGMPHistory", back_populates="ipo", cascade="all, delete-orphan")
    documents = relationship("IPODocument", back_populates="ipo", cascade="all, delete-orphan")
    events = relationship("IPOEvent", back_populates="ipo", cascade="all, delete-orphan")

    # Legacy / Compatibility Columns (mapped directly to DB columns)
    open_date = Column(DateTime, nullable=True)
    close_date = Column(DateTime, nullable=True)
    issue_size = Column(Float, nullable=True, default=0.0)

    # Relationships
    gmp = relationship("IPOGMP", back_populates="ipo", uselist=False, cascade="all, delete-orphan")


class IPOSubscription(Base):
    __tablename__ = "ipo_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    ipo_id = Column(Integer, ForeignKey("ipos.id"), unique=True, nullable=False)
    qib = Column(Float, default=0.0)
    nii = Column(Float, default=0.0)
    retail = Column(Float, default=0.0)
    employee = Column(Float, default=0.0)
    shareholder = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    source = Column(String(100), default="NSE Official Data")
    source_url = Column(String(500), nullable=True)
    as_of_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ipo = relationship("IPO", back_populates="subscription")


class IPOSubscriptionHistory(Base):
    __tablename__ = "ipo_subscription_history"

    id = Column(Integer, primary_key=True, index=True)
    ipo_id = Column(Integer, ForeignKey("ipos.id"), nullable=False, index=True)
    qib = Column(Float, default=0.0)
    nii = Column(Float, default=0.0)
    retail = Column(Float, default=0.0)
    employee = Column(Float, default=0.0)
    shareholder = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    date_str = Column(String(50), nullable=True)
    time_str = Column(String(50), nullable=True)
    source = Column(String(100), default="NSE Official Data")
    source_url = Column(String(500), nullable=True)
    captured_at = Column(DateTime, default=datetime.utcnow)

    ipo = relationship("IPO", back_populates="subscription_history")


class IPOGMP(Base):
    __tablename__ = "ipo_gmp"

    id = Column(Integer, primary_key=True, index=True)
    ipo_id = Column(Integer, ForeignKey("ipos.id"), unique=True, nullable=True)
    company_name = Column(String(250), index=True, nullable=False)
    gmp = Column(Float, nullable=True)
    gmp_percent = Column(Float, nullable=True)
    min_gmp = Column(Float, default=0.0)
    max_gmp = Column(Float, default=0.0)
    estimated_listing_price = Column(Float, nullable=True, default=0.0)
    estimated_listing_gain = Column(Float, nullable=True, default=0.0)
    source = Column(String(100), default="Unofficial Market Feeds")
    source_url = Column(String(500), nullable=True)
    disclaimer = Column(
        String(300), 
        default="GMP is unofficial and unregulated. It is not an NSE/BSE price and should not be treated as a guaranteed listing indicator."
    )
    timestamp = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ipo = relationship("IPO", back_populates="gmp")

    @property
    def indicative_listing_price(self):
        return self.estimated_listing_price


class IPOGMPHistory(Base):
    __tablename__ = "ipo_gmp_history"

    id = Column(Integer, primary_key=True, index=True)
    ipo_id = Column(Integer, ForeignKey("ipos.id"), nullable=False, index=True)
    company_name = Column(String(250), nullable=False)
    gmp = Column(Float, nullable=False)
    gmp_percent = Column(Float, nullable=False)
    min_gmp = Column(Float, default=0.0)
    max_gmp = Column(Float, default=0.0)
    source = Column(String(100), default="Unofficial Market Feeds")
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    ipo = relationship("IPO", back_populates="gmp_history")


class IPODocument(Base):
    __tablename__ = "ipo_documents"

    id = Column(Integer, primary_key=True, index=True)
    ipo_id = Column(Integer, ForeignKey("ipos.id"), nullable=False, index=True)
    document_type = Column(String(50), nullable=False)  # RHP, DRHP, Prospectus, SEBI, NSE, BSE, Registrar
    title = Column(String(250), nullable=False)
    url = Column(String(500), nullable=False)
    verified_at = Column(DateTime, default=datetime.utcnow)

    ipo = relationship("IPO", back_populates="documents")


class IPOEvent(Base):
    __tablename__ = "ipo_events"

    id = Column(Integer, primary_key=True, index=True)
    ipo_id = Column(Integer, ForeignKey("ipos.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)     # Announcement, Open, Close, Allotment, Refund, DematCredit, Listing
    title = Column(String(250), nullable=False)
    event_date = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    source = Column(String(100), default="NSE / Exchange Circular")

    ipo = relationship("IPO", back_populates="events")


class IPODataHealth(Base):
    __tablename__ = "ipo_data_health"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(100), nullable=False, index=True) # NSE Official, BSE Official, SEBI, Unofficial GMP
    status = Column(String(50), default="Healthy")                  # Healthy, Degraded, Down
    last_successful_fetch = Column(DateTime, nullable=True)
    last_failed_fetch = Column(DateTime, nullable=True)
    total_records = Column(Integer, default=0)
    verified_records = Column(Integer, default=0)
    stale_records = Column(Integer, default=0)
    rejected_records = Column(Integer, default=0)
    missing_fields_records = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    target_identifier = Column(String(100), index=True, nullable=False)  # Symbol or IPO Name
    target_type = Column(String(20), default="stock")                   # stock, ipo
    timeframe = Column(String(20), default="next_day")                  # next_day, 5_day, 20_day, listing
    positive_prob = Column(Float, nullable=False)                       # 0 to 100%
    expected_return_min = Column(Float, nullable=False)                 # %
    expected_return_max = Column(Float, nullable=False)                 # %
    confidence = Column(String(20), default="Medium")                   # Low, Medium, High
    model_name = Column(String(50), default="RandomForest")
    features_used = Column(Text, nullable=False)                        # JSON list
    metrics = Column(Text, nullable=False)                              # JSON dict of accuracy, MAE, RMSE, precision, etc.
    validation_method = Column(String(100), default="TimeSeriesSplit Walk-Forward")
    training_period = Column(String(100), default="Historical 2-Year Window")
    created_at = Column(DateTime, default=datetime.utcnow)


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    source = Column(String(100), nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow)
    url = Column(String(500), nullable=True)
    related_stock = Column(String(50), index=True, nullable=True)
    category = Column(String(100), default="Markets")
    sentiment = Column(String(20), default="Neutral")                  # Positive, Neutral, Negative
    sentiment_score = Column(Float, default=0.0)                       # -1.0 to +1.0
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="My Watchlist")
    symbol = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(50), nullable=False)                    # Symbol or IPO Name
    alert_type = Column(String(50), nullable=False)                    # price_above, price_below, pct_change, 52w_high, ipo_open, gmp_change
    condition = Column(String(50), nullable=False)
    threshold = Column(Float, default=0.0)
    is_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    buy_price = Column(Float, nullable=False)
    buy_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketQuote(Base):
    __tablename__ = "market_quotes"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    instrument_type = Column(String(20), default="EQUITY")  # EQUITY, ETF
    exchange = Column(String(20), default="NSE")
    price = Column(Float, nullable=False)
    previous_close = Column(Float, nullable=False)
    change = Column(Float, nullable=False)
    change_percent = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    timestamp = Column(DateTime, nullable=False, index=True)
    source = Column(String(100), nullable=False)
    status = Column(String(50), default="Verified")  # Verified, Delayed, Cached, Needs Verification
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_market_quote_lookup", "symbol", "timestamp", "exchange"),
    )


class IndexQuote(Base):
    __tablename__ = "index_quotes"

    id = Column(Integer, primary_key=True, index=True)
    index_name = Column(String(50), nullable=False, index=True)  # NIFTY 50, SENSEX, NIFTY BANK, etc.
    value = Column(Float, nullable=False)
    previous_close = Column(Float, nullable=False)
    change = Column(Float, nullable=False)
    change_percent = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    source = Column(String(100), nullable=False)
    status = Column(String(50), default="Verified")  # Verified, Delayed, Cached, Needs Verification
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_index_quote_lookup", "index_name", "timestamp"),
    )

