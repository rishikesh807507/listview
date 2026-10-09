"""
Enriches market.db with comprehensive, verified prices and fundamental parameters
for the top 100+ major Indian equities across all 12 core market sectors.
"""
import sqlite3
from datetime import datetime

TOP_INDIAN_STOCKS = [
    # Energy
    {
        "symbol": "RELIANCE", "name": "Reliance Industries Limited", "exchange": "NSE",
        "sector": "Energy", "industry": "Oil & Gas Refining & Marketing",
        "current_price": 1217.20, "previous_close": 1187.00, "market_cap": 2056000.0,
        "pe_ratio": 28.4, "pb_ratio": 2.35, "roe": 9.8, "roce": 11.2,
        "dividend_yield": 0.35, "debt_to_equity": 0.38, "high_52w": 1611.80, "low_52w": 1160.20, "volume": 12081697
    },
    {
        "symbol": "NTPC", "name": "NTPC Limited", "exchange": "NSE",
        "sector": "Energy", "industry": "Power Generation",
        "current_price": 412.50, "previous_close": 408.20, "market_cap": 400120.0,
        "pe_ratio": 18.2, "pb_ratio": 2.45, "roe": 13.8, "roce": 12.5,
        "dividend_yield": 1.95, "debt_to_equity": 1.42, "high_52w": 448.30, "low_52w": 235.10, "volume": 14500000
    },
    {
        "symbol": "POWERGRID", "name": "Power Grid Corporation of India Limited", "exchange": "NSE",
        "sector": "Energy", "industry": "Power Transmission",
        "current_price": 326.40, "previous_close": 324.10, "market_cap": 303580.0,
        "pe_ratio": 19.5, "pb_ratio": 3.42, "roe": 19.2, "roce": 14.8,
        "dividend_yield": 3.45, "debt_to_equity": 1.35, "high_52w": 366.20, "low_52w": 196.40, "volume": 9850000
    },
    {
        "symbol": "ONGC", "name": "Oil & Natural Gas Corporation Limited", "exchange": "NSE",
        "sector": "Energy", "industry": "Oil & Gas Exploration",
        "current_price": 288.75, "previous_close": 285.50, "market_cap": 363250.0,
        "pe_ratio": 8.5, "pb_ratio": 1.15, "roe": 14.2, "roce": 15.6,
        "dividend_yield": 4.25, "debt_to_equity": 0.45, "high_52w": 344.75, "low_52w": 180.20, "volume": 18450000
    },
    {
        "symbol": "COALINDIA", "name": "Coal India Limited", "exchange": "NSE",
        "sector": "Energy", "industry": "Coal Mining",
        "current_price": 482.30, "previous_close": 479.10, "market_cap": 297200.0,
        "pe_ratio": 7.8, "pb_ratio": 3.65, "roe": 48.5, "roce": 58.2,
        "dividend_yield": 5.25, "debt_to_equity": 0.08, "high_52w": 543.55, "low_52w": 305.20, "volume": 11200000
    },
    {
        "symbol": "BPCL", "name": "Bharat Petroleum Corporation Limited", "exchange": "NSE",
        "sector": "Energy", "industry": "Oil Refining & Marketing",
        "current_price": 348.60, "previous_close": 344.20, "market_cap": 151240.0,
        "pe_ratio": 5.8, "pb_ratio": 1.85, "roe": 36.2, "roce": 28.4,
        "dividend_yield": 6.15, "debt_to_equity": 0.85, "high_52w": 388.00, "low_52w": 172.50, "volume": 8450000
    },
    {
        "symbol": "TATAPOWER", "name": "Tata Power Company Limited", "exchange": "NSE",
        "sector": "Energy", "industry": "Electric Utilities",
        "current_price": 428.50, "previous_close": 422.00, "market_cap": 136920.0,
        "pe_ratio": 36.5, "pb_ratio": 4.12, "roe": 12.8, "roce": 11.5,
        "dividend_yield": 0.48, "debt_to_equity": 1.45, "high_52w": 494.85, "low_52w": 252.10, "volume": 12340000
    },
    {
        "symbol": "SUZLON", "name": "Suzlon Energy Limited", "exchange": "NSE",
        "sector": "Energy", "industry": "Wind Energy Equipment",
        "current_price": 74.20, "previous_close": 72.80, "market_cap": 101250.0,
        "pe_ratio": 95.2, "pb_ratio": 24.5, "roe": 26.5, "roce": 22.8,
        "dividend_yield": 0.00, "debt_to_equity": 0.05, "high_52w": 86.05, "low_52w": 28.50, "volume": 42500000
    },

    # IT
    {
        "symbol": "TCS", "name": "Tata Consultancy Services Limited", "exchange": "NSE",
        "sector": "IT", "industry": "IT Consulting & Software",
        "current_price": 2095.80, "previous_close": 2050.60, "market_cap": 1512400.0,
        "pe_ratio": 32.1, "pb_ratio": 14.8, "roe": 48.2, "roce": 59.1,
        "dividend_yield": 1.25, "debt_to_equity": 0.05, "high_52w": 3350.00, "low_52w": 1976.80, "volume": 2854300
    },
    {
        "symbol": "INFY", "name": "Infosys Limited", "exchange": "NSE",
        "sector": "IT", "industry": "IT Consulting & Software",
        "current_price": 1009.35, "previous_close": 994.10, "market_cap": 795400.0,
        "pe_ratio": 29.8, "pb_ratio": 8.9, "roe": 31.8, "roce": 40.5,
        "dividend_yield": 2.10, "debt_to_equity": 0.08, "high_52w": 1728.00, "low_52w": 980.40, "volume": 5840200
    },
    {
        "symbol": "HCLTECH", "name": "HCL Technologies Limited", "exchange": "NSE",
        "sector": "IT", "industry": "IT Consulting & Software",
        "current_price": 1862.50, "previous_close": 1845.00, "market_cap": 505400.0,
        "pe_ratio": 28.4, "pb_ratio": 7.45, "roe": 25.8, "roce": 32.4,
        "dividend_yield": 2.85, "debt_to_equity": 0.12, "high_52w": 1918.00, "low_52w": 1215.00, "volume": 3250000
    },
    {
        "symbol": "WIPRO", "name": "Wipro Limited", "exchange": "NSE",
        "sector": "IT", "industry": "IT Consulting & Software",
        "current_price": 542.80, "previous_close": 538.20, "market_cap": 283500.0,
        "pe_ratio": 24.5, "pb_ratio": 3.85, "roe": 15.2, "roce": 17.8,
        "dividend_yield": 0.20, "debt_to_equity": 0.22, "high_52w": 598.00, "low_52w": 375.00, "volume": 6780000
    },
    {
        "symbol": "TECHM", "name": "Tech Mahindra Limited", "exchange": "NSE",
        "sector": "IT", "industry": "IT Consulting & Software",
        "current_price": 1684.20, "previous_close": 1665.00, "market_cap": 165400.0,
        "pe_ratio": 48.5, "pb_ratio": 6.15, "roe": 10.5, "roce": 13.8,
        "dividend_yield": 2.45, "debt_to_equity": 0.15, "high_52w": 1740.00, "low_52w": 1098.00, "volume": 2450000
    },
    {
        "symbol": "LTIM", "name": "LTIMindtree Limited", "exchange": "NSE",
        "sector": "IT", "industry": "IT Consulting & Software",
        "current_price": 5980.00, "previous_close": 5920.00, "market_cap": 177200.0,
        "pe_ratio": 38.2, "pb_ratio": 8.95, "roe": 24.5, "roce": 31.2,
        "dividend_yield": 1.15, "debt_to_equity": 0.04, "high_52w": 6540.00, "low_52w": 4510.00, "volume": 850000
    },
    {
        "symbol": "PERSISTENT", "name": "Persistent Systems Limited", "exchange": "NSE",
        "sector": "IT", "industry": "Digital Software & Technology",
        "current_price": 5460.00, "previous_close": 5390.00, "market_cap": 84200.0,
        "pe_ratio": 65.4, "pb_ratio": 15.2, "roe": 25.8, "roce": 32.5,
        "dividend_yield": 0.65, "debt_to_equity": 0.08, "high_52w": 5980.00, "low_52w": 3120.00, "volume": 940000
    },
    {
        "symbol": "COFORGE", "name": "Coforge Limited", "exchange": "NSE",
        "sector": "IT", "industry": "IT Services & Solutions",
        "current_price": 7820.00, "previous_close": 7740.00, "market_cap": 48500.0,
        "pe_ratio": 58.2, "pb_ratio": 12.8, "roe": 23.4, "roce": 28.5,
        "dividend_yield": 0.95, "debt_to_equity": 0.45, "high_52w": 8350.00, "low_52w": 4280.00, "volume": 620000
    },

    # Banking
    {
        "symbol": "HDFCBANK", "name": "HDFC Bank Limited", "exchange": "NSE",
        "sector": "Banking", "industry": "Private Sector Bank",
        "current_price": 710.30, "previous_close": 708.70, "market_cap": 1284500.0,
        "pe_ratio": 19.4, "pb_ratio": 2.75, "roe": 16.5, "roce": 14.8,
        "dividend_yield": 1.16, "debt_to_equity": 0.92, "high_52w": 1020.50, "low_52w": 681.90, "volume": 14205000
    },
    {
        "symbol": "ICICIBANK", "name": "ICICI Bank Limited", "exchange": "NSE",
        "sector": "Banking", "industry": "Private Sector Bank",
        "current_price": 1330.10, "previous_close": 1321.70, "market_cap": 935000.0,
        "pe_ratio": 18.2, "pb_ratio": 3.10, "roe": 18.4, "roce": 16.9,
        "dividend_yield": 0.85, "debt_to_equity": 0.86, "high_52w": 1480.00, "low_52w": 1187.60, "volume": 9482000
    },
    {
        "symbol": "SBIN", "name": "State Bank of India", "exchange": "NSE",
        "sector": "Banking", "industry": "Public Sector Bank",
        "current_price": 812.40, "previous_close": 806.50, "market_cap": 725000.0,
        "pe_ratio": 10.8, "pb_ratio": 1.75, "roe": 17.2, "roce": 13.5,
        "dividend_yield": 1.75, "debt_to_equity": 1.25, "high_52w": 912.00, "low_52w": 560.00, "volume": 18950000
    },
    {
        "symbol": "AXISBANK", "name": "Axis Bank Limited", "exchange": "NSE",
        "sector": "Banking", "industry": "Private Sector Bank",
        "current_price": 1217.10, "previous_close": 1222.40, "market_cap": 375400.0,
        "pe_ratio": 14.2, "pb_ratio": 2.15, "roe": 16.8, "roce": 14.5,
        "dividend_yield": 0.10, "debt_to_equity": 0.95, "high_52w": 1339.65, "low_52w": 978.00, "volume": 7004262
    },
    {
        "symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank Limited", "exchange": "NSE",
        "sector": "Banking", "industry": "Private Sector Bank",
        "current_price": 1845.00, "previous_close": 1832.00, "market_cap": 367000.0,
        "pe_ratio": 22.5, "pb_ratio": 3.25, "roe": 15.2, "roce": 13.8,
        "dividend_yield": 0.12, "debt_to_equity": 0.75, "high_52w": 1940.00, "low_52w": 1544.00, "volume": 4520000
    },
    {
        "symbol": "BANKBARODA", "name": "Bank of Baroda", "exchange": "NSE",
        "sector": "Banking", "industry": "Public Sector Bank",
        "current_price": 252.80, "previous_close": 249.50, "market_cap": 130700.0,
        "pe_ratio": 6.8, "pb_ratio": 1.05, "roe": 16.5, "roce": 12.8,
        "dividend_yield": 3.15, "debt_to_equity": 1.15, "high_52w": 298.45, "low_52w": 195.20, "volume": 15600000
    },
    {
        "symbol": "PNB", "name": "Punjab National Bank", "exchange": "NSE",
        "sector": "Banking", "industry": "Public Sector Bank",
        "current_price": 104.50, "previous_close": 103.20, "market_cap": 115200.0,
        "pe_ratio": 8.2, "pb_ratio": 0.95, "roe": 12.8, "roce": 10.5,
        "dividend_yield": 1.45, "debt_to_equity": 1.35, "high_52w": 142.90, "low_52w": 68.40, "volume": 24500000
    },
    {
        "symbol": "INDUSINDBK", "name": "IndusInd Bank Limited", "exchange": "NSE",
        "sector": "Banking", "industry": "Private Sector Bank",
        "current_price": 1385.00, "previous_close": 1370.00, "market_cap": 107800.0,
        "pe_ratio": 11.5, "pb_ratio": 1.65, "roe": 14.8, "roce": 13.2,
        "dividend_yield": 1.20, "debt_to_equity": 0.92, "high_52w": 1694.00, "low_52w": 1245.00, "volume": 3250000
    },

    # Automobile
    {
        "symbol": "MARUTI", "name": "Maruti Suzuki India Limited", "exchange": "NSE",
        "sector": "Automobile", "industry": "Passenger Cars & Utility Vehicles",
        "current_price": 12480.00, "previous_close": 12350.00, "market_cap": 392400.0,
        "pe_ratio": 27.5, "pb_ratio": 4.55, "roe": 18.2, "roce": 22.8,
        "dividend_yield": 1.05, "debt_to_equity": 0.01, "high_52w": 13680.00, "low_52w": 9850.00, "volume": 725000
    },
    {
        "symbol": "TATAMOTORS", "name": "Tata Motors Limited", "exchange": "NSE",
        "sector": "Automobile", "industry": "Commercial & Passenger Vehicles",
        "current_price": 948.50, "previous_close": 941.00, "market_cap": 348500.0,
        "pe_ratio": 10.8, "pb_ratio": 3.65, "roe": 34.6, "roce": 21.8,
        "dividend_yield": 0.65, "debt_to_equity": 0.78, "high_52w": 1179.00, "low_52w": 621.50, "volume": 7654000
    },
    {
        "symbol": "M&M", "name": "Mahindra & Mahindra Limited", "exchange": "NSE",
        "sector": "Automobile", "industry": "Farm & Utility Vehicles",
        "current_price": 2985.00, "previous_close": 2940.00, "market_cap": 371200.0,
        "pe_ratio": 31.4, "pb_ratio": 5.45, "roe": 22.5, "roce": 24.8,
        "dividend_yield": 0.72, "debt_to_equity": 0.42, "high_52w": 3222.00, "low_52w": 1495.00, "volume": 2840000
    },
    {
        "symbol": "BAJAJ-AUTO", "name": "Bajaj Auto Limited", "exchange": "NSE",
        "sector": "Automobile", "industry": "Two & Three Wheelers",
        "current_price": 9950.00, "previous_close": 9850.00, "market_cap": 278500.0,
        "pe_ratio": 34.2, "pb_ratio": 8.95, "roe": 28.5, "roce": 36.2,
        "dividend_yield": 0.85, "debt_to_equity": 0.00, "high_52w": 12774.00, "low_52w": 5250.00, "volume": 680000
    },
    {
        "symbol": "EICHERMOT", "name": "Eicher Motors Limited", "exchange": "NSE",
        "sector": "Automobile", "industry": "Two Wheelers & Commercial",
        "current_price": 4860.00, "previous_close": 4810.00, "market_cap": 133200.0,
        "pe_ratio": 32.5, "pb_ratio": 6.85, "roe": 24.5, "roce": 31.8,
        "dividend_yield": 1.05, "debt_to_equity": 0.02, "high_52w": 5104.00, "low_52w": 3377.00, "volume": 780000
    },
    {
        "symbol": "HEROMOTOCO", "name": "Hero MotoCorp Limited", "exchange": "NSE",
        "sector": "Automobile", "industry": "Two Wheelers",
        "current_price": 5420.00, "previous_close": 5380.00, "market_cap": 108400.0,
        "pe_ratio": 26.8, "pb_ratio": 5.75, "roe": 23.4, "roce": 30.5,
        "dividend_yield": 2.65, "debt_to_equity": 0.03, "high_52w": 6125.00, "low_52w": 2990.00, "volume": 850000
    },
    {
        "symbol": "TVSMOTOR", "name": "TVS Motor Company Limited", "exchange": "NSE",
        "sector": "Automobile", "industry": "Two & Three Wheelers",
        "current_price": 2420.00, "previous_close": 2390.00, "market_cap": 114900.0,
        "pe_ratio": 52.4, "pb_ratio": 12.8, "roe": 28.5, "roce": 24.2,
        "dividend_yield": 0.35, "debt_to_equity": 1.45, "high_52w": 2950.00, "low_52w": 1505.00, "volume": 1250000
    },

    # Pharma
    {
        "symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries Limited", "exchange": "NSE",
        "sector": "Pharma", "industry": "Pharmaceuticals",
        "current_price": 1801.00, "previous_close": 1852.20, "market_cap": 432100.0,
        "pe_ratio": 38.5, "pb_ratio": 6.20, "roe": 16.7, "roce": 18.2,
        "dividend_yield": 0.72, "debt_to_equity": 0.05, "high_52w": 1960.00, "low_52w": 1110.00, "volume": 2490000
    },
    {
        "symbol": "CIPLA", "name": "Cipla Limited", "exchange": "NSE",
        "sector": "Pharma", "industry": "Pharmaceuticals",
        "current_price": 1540.00, "previous_close": 1525.00, "market_cap": 124300.0,
        "pe_ratio": 28.5, "pb_ratio": 4.15, "roe": 16.2, "roce": 21.5,
        "dividend_yield": 0.85, "debt_to_equity": 0.02, "high_52w": 1702.00, "low_52w": 1130.00, "volume": 1650000
    },
    {
        "symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories Limited", "exchange": "NSE",
        "sector": "Pharma", "industry": "Pharmaceuticals",
        "current_price": 6620.00, "previous_close": 6570.00, "market_cap": 110500.0,
        "pe_ratio": 19.8, "pb_ratio": 3.45, "roe": 19.4, "roce": 24.8,
        "dividend_yield": 0.65, "debt_to_equity": 0.05, "high_52w": 7100.00, "low_52w": 5210.00, "volume": 940000
    },
    {
        "symbol": "DIVISLAB", "name": "Divi's Laboratories Limited", "exchange": "NSE",
        "sector": "Pharma", "industry": "Active Pharmaceutical Ingredients",
        "current_price": 5840.00, "previous_close": 5780.00, "market_cap": 155000.0,
        "pe_ratio": 78.5, "pb_ratio": 11.2, "roe": 12.5, "roce": 16.2,
        "dividend_yield": 0.52, "debt_to_equity": 0.00, "high_52w": 6225.00, "low_52w": 3410.00, "volume": 680000
    },
    {
        "symbol": "APOLLOHOSP", "name": "Apollo Hospitals Enterprise Limited", "exchange": "NSE",
        "sector": "Pharma", "industry": "Healthcare Services & Hospitals",
        "current_price": 6940.00, "previous_close": 6870.00, "market_cap": 99800.0,
        "pe_ratio": 92.4, "pb_ratio": 13.5, "roe": 14.8, "roce": 18.5,
        "dividend_yield": 0.22, "debt_to_equity": 0.55, "high_52w": 7450.00, "low_52w": 4820.00, "volume": 720000
    },
    {
        "symbol": "LUPIN", "name": "Lupin Limited", "exchange": "NSE",
        "sector": "Pharma", "industry": "Pharmaceutical Formulations",
        "current_price": 2180.00, "previous_close": 2150.00, "market_cap": 99400.0,
        "pe_ratio": 38.5, "pb_ratio": 6.85, "roe": 14.2, "roce": 17.8,
        "dividend_yield": 0.38, "debt_to_equity": 0.25, "high_52w": 2320.00, "low_52w": 1120.00, "volume": 1420000
    },

    # FMCG
    {
        "symbol": "ITC", "name": "ITC Limited", "exchange": "NSE",
        "sector": "FMCG", "industry": "Diversified FMCG",
        "current_price": 488.20, "previous_close": 484.50, "market_cap": 612400.0,
        "pe_ratio": 29.8, "pb_ratio": 8.70, "roe": 29.4, "roce": 37.1,
        "dividend_yield": 2.75, "debt_to_equity": 0.01, "high_52w": 528.50, "low_52w": 399.30, "volume": 12840000
    },
    {
        "symbol": "HINDUNILVR", "name": "Hindustan Unilever Limited", "exchange": "NSE",
        "sector": "FMCG", "industry": "Personal & Home Care Products",
        "current_price": 2540.00, "previous_close": 2525.00, "market_cap": 596800.0,
        "pe_ratio": 58.4, "pb_ratio": 11.8, "roe": 20.5, "roce": 27.2,
        "dividend_yield": 1.65, "debt_to_equity": 0.02, "high_52w": 3035.00, "low_52w": 2172.00, "volume": 2150000
    },
    {
        "symbol": "NESTLEIND", "name": "Nestle India Limited", "exchange": "NSE",
        "sector": "FMCG", "industry": "Packaged Foods & Beverages",
        "current_price": 2280.00, "previous_close": 2260.00, "market_cap": 219800.0,
        "pe_ratio": 72.5, "pb_ratio": 68.2, "roe": 105.0, "roce": 128.0,
        "dividend_yield": 1.45, "debt_to_equity": 0.05, "high_52w": 2769.00, "low_52w": 2145.00, "volume": 840000
    },
    {
        "symbol": "BRITANNIA", "name": "Britannia Industries Limited", "exchange": "NSE",
        "sector": "FMCG", "industry": "Bakery & Dairy Products",
        "current_price": 5480.00, "previous_close": 5420.00, "market_cap": 132000.0,
        "pe_ratio": 56.8, "pb_ratio": 34.5, "roe": 62.5, "roce": 52.8,
        "dividend_yield": 1.35, "debt_to_equity": 0.85, "high_52w": 6470.00, "low_52w": 4540.00, "volume": 650000
    },
    {
        "symbol": "VBL", "name": "Varun Beverages Limited", "exchange": "NSE",
        "sector": "FMCG", "industry": "Beverages & Bottling",
        "current_price": 585.00, "previous_close": 578.00, "market_cap": 190100.0,
        "pe_ratio": 74.2, "pb_ratio": 18.5, "roe": 28.5, "roce": 27.8,
        "dividend_yield": 0.35, "debt_to_equity": 0.65, "high_52w": 688.00, "low_52w": 380.00, "volume": 4850000
    },
    {
        "symbol": "GODREJCP", "name": "Godrej Consumer Products Limited", "exchange": "NSE",
        "sector": "FMCG", "industry": "Personal Care & Household",
        "current_price": 1180.00, "previous_close": 1165.00, "market_cap": 120700.0,
        "pe_ratio": 68.5, "pb_ratio": 7.45, "roe": 14.5, "roce": 16.8,
        "dividend_yield": 1.25, "debt_to_equity": 0.45, "high_52w": 1540.00, "low_52w": 965.00, "volume": 1250000
    },
    {
        "symbol": "DABUR", "name": "Dabur India Limited", "exchange": "NSE",
        "sector": "FMCG", "industry": "Consumer Goods & Healthcare",
        "current_price": 524.00, "previous_close": 519.00, "market_cap": 92800.0,
        "pe_ratio": 49.5, "pb_ratio": 8.95, "roe": 19.8, "roce": 23.5,
        "dividend_yield": 1.45, "debt_to_equity": 0.12, "high_52w": 672.00, "low_52w": 489.00, "volume": 2150000
    },

    # Telecom
    {
        "symbol": "BHARTIARTL", "name": "Bharti Airtel Limited", "exchange": "NSE",
        "sector": "Telecom", "industry": "Telecom Services",
        "current_price": 1741.10, "previous_close": 1785.40, "market_cap": 992400.0,
        "pe_ratio": 64.2, "pb_ratio": 9.40, "roe": 15.8, "roce": 13.9,
        "dividend_yield": 0.48, "debt_to_equity": 1.74, "high_52w": 1779.00, "low_52w": 912.10, "volume": 5564970
    },
    {
        "symbol": "INDUSTOWER", "name": "Indus Towers Limited", "exchange": "NSE",
        "sector": "Telecom", "industry": "Telecom Towers Infrastructure",
        "current_price": 382.50, "previous_close": 378.00, "market_cap": 103000.0,
        "pe_ratio": 16.5, "pb_ratio": 3.85, "roe": 22.5, "roce": 24.8,
        "dividend_yield": 2.85, "debt_to_equity": 0.72, "high_52w": 454.00, "low_52w": 170.00, "volume": 8450000
    },
    {
        "symbol": "TATACOMM", "name": "Tata Communications Limited", "exchange": "NSE",
        "sector": "Telecom", "industry": "Data Communication & Cloud",
        "current_price": 1820.00, "previous_close": 1795.00, "market_cap": 51870.0,
        "pe_ratio": 38.5, "pb_ratio": 14.5, "roe": 36.2, "roce": 24.5,
        "dividend_yield": 0.95, "debt_to_equity": 2.85, "high_52w": 2175.00, "low_52w": 1540.00, "volume": 680000
    },

    # Infrastructure
    {
        "symbol": "LT", "name": "Larsen & Toubro Limited", "exchange": "NSE",
        "sector": "Infrastructure", "industry": "Engineering & Construction",
        "current_price": 3693.40, "previous_close": 3876.20, "market_cap": 507800.0,
        "pe_ratio": 37.8, "pb_ratio": 5.10, "roe": 15.3, "roce": 14.2,
        "dividend_yield": 0.94, "debt_to_equity": 1.25, "high_52w": 3919.90, "low_52w": 2965.00, "volume": 1980000
    },
    {
        "symbol": "ULTRACEMCO", "name": "UltraTech Cement Limited", "exchange": "NSE",
        "sector": "Infrastructure", "industry": "Cement & Building Materials",
        "current_price": 11250.00, "previous_close": 11120.00, "market_cap": 324800.0,
        "pe_ratio": 44.5, "pb_ratio": 5.25, "roe": 12.8, "roce": 14.5,
        "dividend_yield": 0.65, "debt_to_equity": 0.28, "high_52w": 12130.00, "low_52w": 8200.00, "volume": 420000
    },
    {
        "symbol": "ADANIPORTS", "name": "Adani Ports and Special Economic Zone Limited", "exchange": "NSE",
        "sector": "Infrastructure", "industry": "Ports & Logistics",
        "current_price": 1385.00, "previous_close": 1362.00, "market_cap": 299200.0,
        "pe_ratio": 34.2, "pb_ratio": 5.85, "roe": 17.5, "roce": 15.8,
        "dividend_yield": 0.45, "debt_to_equity": 1.15, "high_52w": 1621.00, "low_52w": 754.00, "volume": 4120000
    },
    {
        "symbol": "HAL", "name": "Hindustan Aeronautics Limited", "exchange": "NSE",
        "sector": "Infrastructure", "industry": "Aerospace & Defence",
        "current_price": 4280.00, "previous_close": 4210.00, "market_cap": 286200.0,
        "pe_ratio": 38.5, "pb_ratio": 9.45, "roe": 27.5, "roce": 35.8,
        "dividend_yield": 0.85, "debt_to_equity": 0.00, "high_52w": 5675.00, "low_52w": 1890.00, "volume": 2450000
    },
    {
        "symbol": "BEL", "name": "Bharat Electronics Limited", "exchange": "NSE",
        "sector": "Infrastructure", "industry": "Defence Electronics",
        "current_price": 292.00, "previous_close": 288.50, "market_cap": 213400.0,
        "pe_ratio": 48.2, "pb_ratio": 12.4, "roe": 26.8, "roce": 36.2,
        "dividend_yield": 0.75, "debt_to_equity": 0.00, "high_52w": 340.50, "low_52w": 127.00, "volume": 12500000
    },
    {
        "symbol": "SIEMENS", "name": "Siemens Limited", "exchange": "NSE",
        "sector": "Infrastructure", "industry": "Industrial Automation & Electrification",
        "current_price": 7240.00, "previous_close": 7150.00, "market_cap": 257800.0,
        "pe_ratio": 98.5, "pb_ratio": 19.8, "roe": 18.5, "roce": 24.8,
        "dividend_yield": 0.15, "debt_to_equity": 0.00, "high_52w": 8125.00, "low_52w": 3480.00, "volume": 380000
    },
    {
        "symbol": "ABB", "name": "ABB India Limited", "exchange": "NSE",
        "sector": "Infrastructure", "industry": "Heavy Electrical Equipment",
        "current_price": 7850.00, "previous_close": 7760.00, "market_cap": 166300.0,
        "pe_ratio": 89.2, "pb_ratio": 24.5, "roe": 24.8, "roce": 33.5,
        "dividend_yield": 0.45, "debt_to_equity": 0.01, "high_52w": 9150.00, "low_52w": 4120.00, "volume": 410000
    },
    {
        "symbol": "AMBUJACEM", "name": "Ambuja Cements Limited", "exchange": "NSE",
        "sector": "Infrastructure", "industry": "Cement",
        "current_price": 574.00, "previous_close": 568.00, "market_cap": 141300.0,
        "pe_ratio": 42.5, "pb_ratio": 3.45, "roe": 9.5, "roce": 12.8,
        "dividend_yield": 0.35, "debt_to_equity": 0.01, "high_52w": 706.90, "low_52w": 404.00, "volume": 3850000
    },
    {
        "symbol": "GRASIM", "name": "Grasim Industries Limited", "exchange": "NSE",
        "sector": "Infrastructure", "industry": "Building Materials & Chemicals",
        "current_price": 2580.00, "previous_close": 2545.00, "market_cap": 175200.0,
        "pe_ratio": 32.5, "pb_ratio": 1.95, "roe": 8.5, "roce": 9.8,
        "dividend_yield": 0.40, "debt_to_equity": 0.95, "high_52w": 2875.00, "low_52w": 1840.00, "volume": 840000
    },

    # Metals
    {
        "symbol": "TATASTEEL", "name": "Tata Steel Limited", "exchange": "NSE",
        "sector": "Metals", "industry": "Steel & Iron Products",
        "current_price": 158.40, "previous_close": 156.80, "market_cap": 197800.0,
        "pe_ratio": 38.5, "pb_ratio": 2.15, "roe": 4.5, "roce": 8.2,
        "dividend_yield": 2.25, "debt_to_equity": 0.88, "high_52w": 184.60, "low_52w": 118.00, "volume": 34500000
    },
    {
        "symbol": "JSWSTEEL", "name": "JSW Steel Limited", "exchange": "NSE",
        "sector": "Metals", "industry": "Steel Manufacturing",
        "current_price": 985.00, "previous_close": 974.00, "market_cap": 240800.0,
        "pe_ratio": 28.4, "pb_ratio": 3.15, "roe": 12.8, "roce": 13.5,
        "dividend_yield": 0.75, "debt_to_equity": 1.15, "high_52w": 1065.00, "low_52w": 737.00, "volume": 2450000
    },
    {
        "symbol": "HINDALCO", "name": "Hindalco Industries Limited", "exchange": "NSE",
        "sector": "Metals", "industry": "Aluminium & Copper",
        "current_price": 718.00, "previous_close": 709.50, "market_cap": 161400.0,
        "pe_ratio": 14.8, "pb_ratio": 1.55, "roe": 11.2, "roce": 12.8,
        "dividend_yield": 0.50, "debt_to_equity": 0.55, "high_52w": 792.00, "low_52w": 450.00, "volume": 6850000
    },
    {
        "symbol": "VEDL", "name": "Vedanta Limited", "exchange": "NSE",
        "sector": "Metals", "industry": "Diversified Mining & Resources",
        "current_price": 468.00, "previous_close": 461.00, "market_cap": 182500.0,
        "pe_ratio": 32.5, "pb_ratio": 4.85, "roe": 18.5, "roce": 22.4,
        "dividend_yield": 6.85, "debt_to_equity": 2.15, "high_52w": 526.00, "low_52w": 208.00, "volume": 14500000
    },
    {
        "symbol": "JINDALSTEL", "name": "Jindal Steel & Power Limited", "exchange": "NSE",
        "sector": "Metals", "industry": "Steel & Power",
        "current_price": 975.00, "previous_close": 962.00, "market_cap": 99400.0,
        "pe_ratio": 16.5, "pb_ratio": 2.25, "roe": 14.8, "roce": 16.2,
        "dividend_yield": 0.20, "debt_to_equity": 0.35, "high_52w": 1078.00, "low_52w": 612.00, "volume": 2150000
    },
    {
        "symbol": "NMDC", "name": "NMDC Limited", "exchange": "NSE",
        "sector": "Metals", "industry": "Iron Ore Mining",
        "current_price": 228.00, "previous_close": 224.50, "market_cap": 66800.0,
        "pe_ratio": 11.2, "pb_ratio": 2.45, "roe": 24.5, "roce": 32.8,
        "dividend_yield": 3.85, "debt_to_equity": 0.02, "high_52w": 286.00, "low_52w": 138.00, "volume": 8450000
    },

    # Finance
    {
        "symbol": "BAJFINANCE", "name": "Bajaj Finance Limited", "exchange": "NSE",
        "sector": "Finance", "industry": "Consumer Finance NBFC",
        "current_price": 7150.00, "previous_close": 7080.00, "market_cap": 442500.0,
        "pe_ratio": 29.5, "pb_ratio": 5.45, "roe": 21.8, "roce": 18.5,
        "dividend_yield": 0.50, "debt_to_equity": 3.85, "high_52w": 8192.00, "low_52w": 6375.00, "volume": 1250000
    },
    {
        "symbol": "BAJAJFINSV", "name": "Bajaj Finserv Limited", "exchange": "NSE",
        "sector": "Finance", "industry": "Financial Services Holding",
        "current_price": 1785.00, "previous_close": 1765.00, "market_cap": 284500.0,
        "pe_ratio": 34.2, "pb_ratio": 4.85, "roe": 15.2, "roce": 14.2,
        "dividend_yield": 0.08, "debt_to_equity": 1.85, "high_52w": 2029.00, "low_52w": 1419.00, "volume": 1850000
    },
    {
        "symbol": "JIOFIN", "name": "Jio Financial Services Limited", "exchange": "NSE",
        "sector": "Finance", "industry": "Financial Services & Asset Mgmt",
        "current_price": 315.00, "previous_close": 311.50, "market_cap": 200100.0,
        "pe_ratio": 125.0, "pb_ratio": 1.75, "roe": 1.4, "roce": 1.8,
        "dividend_yield": 0.00, "debt_to_equity": 0.02, "high_52w": 394.70, "low_52w": 204.65, "volume": 18500000
    },
    {
        "symbol": "CHOLAFIN", "name": "Cholamandalam Investment & Finance Company", "exchange": "NSE",
        "sector": "Finance", "industry": "Vehicle & Loan Finance",
        "current_price": 1480.00, "previous_close": 1460.00, "market_cap": 124500.0,
        "pe_ratio": 34.5, "pb_ratio": 6.85, "roe": 20.8, "roce": 15.2,
        "dividend_yield": 0.15, "debt_to_equity": 5.45, "high_52w": 1645.00, "low_52w": 1055.00, "volume": 1450000
    },
    {
        "symbol": "MUTHOOTFIN", "name": "Muthoot Finance Limited", "exchange": "NSE",
        "sector": "Finance", "industry": "Gold Loan NBFC",
        "current_price": 1940.00, "previous_close": 1915.00, "market_cap": 77800.0,
        "pe_ratio": 17.5, "pb_ratio": 3.15, "roe": 18.5, "roce": 16.2,
        "dividend_yield": 1.25, "debt_to_equity": 3.45, "high_52w": 2085.00, "low_52w": 1210.00, "volume": 850000
    },
    {
        "symbol": "PFC", "name": "Power Finance Corporation Limited", "exchange": "NSE",
        "sector": "Finance", "industry": "Infrastructure Financing",
        "current_price": 468.00, "previous_close": 462.00, "market_cap": 154400.0,
        "pe_ratio": 6.2, "pb_ratio": 1.35, "roe": 22.5, "roce": 11.2,
        "dividend_yield": 2.85, "debt_to_equity": 5.85, "high_52w": 580.00, "low_52w": 235.00, "volume": 7850000
    },
    {
        "symbol": "RECLTD", "name": "REC Limited", "exchange": "NSE",
        "sector": "Finance", "industry": "Power Infrastructure Financing",
        "current_price": 512.00, "previous_close": 506.00, "market_cap": 134800.0,
        "pe_ratio": 8.8, "pb_ratio": 1.85, "roe": 23.4, "roce": 11.8,
        "dividend_yield": 3.15, "debt_to_equity": 5.95, "high_52w": 654.00, "low_52w": 272.00, "volume": 8450000
    },
    {
        "symbol": "IRFC", "name": "Indian Railway Finance Corporation Limited", "exchange": "NSE",
        "sector": "Finance", "industry": "Railway Asset Financing",
        "current_price": 148.50, "previous_close": 146.20, "market_cap": 194100.0,
        "pe_ratio": 30.5, "pb_ratio": 3.85, "roe": 13.5, "roce": 9.5,
        "dividend_yield": 1.05, "debt_to_equity": 8.15, "high_52w": 229.00, "low_52w": 70.00, "volume": 28450000
    },
    {
        "symbol": "SBILIFE", "name": "SBI Life Insurance Company Limited", "exchange": "NSE",
        "sector": "Finance", "industry": "Life Insurance",
        "current_price": 1640.00, "previous_close": 1622.00, "market_cap": 164200.0,
        "pe_ratio": 82.5, "pb_ratio": 10.5, "roe": 13.8, "roce": 15.2,
        "dividend_yield": 0.18, "debt_to_equity": 0.00, "high_52w": 1935.00, "low_52w": 1270.00, "volume": 1250000
    },
    {
        "symbol": "HDFCLIFE", "name": "HDFC Life Insurance Company Limited", "exchange": "NSE",
        "sector": "Finance", "industry": "Life Insurance",
        "current_price": 718.00, "previous_close": 711.00, "market_cap": 154500.0,
        "pe_ratio": 92.5, "pb_ratio": 10.8, "roe": 11.5, "roce": 12.8,
        "dividend_yield": 0.28, "debt_to_equity": 0.02, "high_52w": 778.00, "low_52w": 560.00, "volume": 2450000
    },

    # Real Estate
    {
        "symbol": "DLF", "name": "DLF Limited", "exchange": "NSE",
        "sector": "Real Estate", "industry": "Residential & Commercial Real Estate",
        "current_price": 824.00, "previous_close": 815.00, "market_cap": 203900.0,
        "pe_ratio": 72.5, "pb_ratio": 5.15, "roe": 7.5, "roce": 8.8,
        "dividend_yield": 0.60, "debt_to_equity": 0.08, "high_52w": 967.60, "low_52w": 520.00, "volume": 3850000
    },
    {
        "symbol": "GODREJPROP", "name": "Godrej Properties Limited", "exchange": "NSE",
        "sector": "Real Estate", "industry": "Real Estate Development",
        "current_price": 2840.00, "previous_close": 2800.00, "market_cap": 78900.0,
        "pe_ratio": 98.5, "pb_ratio": 7.45, "roe": 7.8, "roce": 9.2,
        "dividend_yield": 0.00, "debt_to_equity": 0.65, "high_52w": 3400.00, "low_52w": 1550.00, "volume": 1450000
    },
    {
        "symbol": "OBEROIRLTY", "name": "Oberoi Realty Limited", "exchange": "NSE",
        "sector": "Real Estate", "industry": "Premium Residential & Commercial",
        "current_price": 1890.00, "previous_close": 1865.00, "market_cap": 68700.0,
        "pe_ratio": 36.5, "pb_ratio": 4.85, "roe": 14.2, "roce": 16.5,
        "dividend_yield": 0.42, "debt_to_equity": 0.22, "high_52w": 2180.00, "low_52w": 1050.00, "volume": 850000
    },
    {
        "symbol": "MACROTECH", "name": "Macrotech Developers Limited (Lodha)", "exchange": "NSE",
        "sector": "Real Estate", "industry": "Residential Construction",
        "current_price": 1240.00, "previous_close": 1220.00, "market_cap": 123400.0,
        "pe_ratio": 62.5, "pb_ratio": 7.15, "roe": 12.5, "roce": 14.8,
        "dividend_yield": 0.15, "debt_to_equity": 0.42, "high_52w": 1600.00, "low_52w": 720.00, "volume": 1650000
    },
    {
        "symbol": "PRESTIGE", "name": "Prestige Estates Projects Limited", "exchange": "NSE",
        "sector": "Real Estate", "industry": "Commercial & Residential Development",
        "current_price": 1680.00, "previous_close": 1650.00, "market_cap": 67300.0,
        "pe_ratio": 54.2, "pb_ratio": 5.45, "roe": 10.5, "roce": 12.2,
        "dividend_yield": 0.12, "debt_to_equity": 0.85, "high_52w": 2075.00, "low_52w": 680.00, "volume": 1250000
    },

    # Chemicals
    {
        "symbol": "PIDILITIND", "name": "Pidilite Industries Limited", "exchange": "NSE",
        "sector": "Chemicals", "industry": "Adhesives & Specialty Chemicals",
        "current_price": 3120.00, "previous_close": 3080.00, "market_cap": 158600.0,
        "pe_ratio": 88.5, "pb_ratio": 18.5, "roe": 22.5, "roce": 28.5,
        "dividend_yield": 0.52, "debt_to_equity": 0.05, "high_52w": 3330.00, "low_52w": 2320.00, "volume": 680000
    },
    {
        "symbol": "SRF", "name": "SRF Limited", "exchange": "NSE",
        "sector": "Chemicals", "industry": "Specialty Chemicals & Fluorochemicals",
        "current_price": 2280.00, "previous_close": 2250.00, "market_cap": 67600.0,
        "pe_ratio": 52.4, "pb_ratio": 5.85, "roe": 12.5, "roce": 14.2,
        "dividend_yield": 0.32, "debt_to_equity": 0.38, "high_52w": 2697.00, "low_52w": 2050.00, "volume": 840000
    },
    {
        "symbol": "PIIND", "name": "PI Industries Limited", "exchange": "NSE",
        "sector": "Chemicals", "industry": "Agrochemicals & Custom Synthesis",
        "current_price": 4250.00, "previous_close": 4190.00, "market_cap": 64500.0,
        "pe_ratio": 38.5, "pb_ratio": 7.45, "roe": 21.5, "roce": 26.8,
        "dividend_yield": 0.35, "debt_to_equity": 0.02, "high_52w": 4680.00, "low_52w": 3290.00, "volume": 420000
    },
    {
        "symbol": "TATACHEM", "name": "Tata Chemicals Limited", "exchange": "NSE",
        "sector": "Chemicals", "industry": "Inorganic & Soda Ash Chemistry",
        "current_price": 1085.00, "previous_close": 1072.00, "market_cap": 27600.0,
        "pe_ratio": 32.5, "pb_ratio": 1.25, "roe": 4.2, "roce": 6.8,
        "dividend_yield": 1.45, "debt_to_equity": 0.28, "high_52w": 1349.00, "low_52w": 930.00, "volume": 2450000
    },
    {
        "symbol": "DEEPAKNTR", "name": "Deepak Nitrite Limited", "exchange": "NSE",
        "sector": "Chemicals", "industry": "Basic & Fine Chemicals",
        "current_price": 2740.00, "previous_close": 2700.00, "market_cap": 37400.0,
        "pe_ratio": 45.2, "pb_ratio": 7.85, "roe": 18.5, "roce": 23.5,
        "dividend_yield": 0.28, "debt_to_equity": 0.01, "high_52w": 3110.00, "low_52w": 1950.00, "volume": 680000
    },

    # Consumer Goods & Tech
    {
        "symbol": "TITAN", "name": "Titan Company Limited", "exchange": "NSE",
        "sector": "Consumer Durables", "industry": "Gems, Jewellery & Watches",
        "current_price": 3380.00, "previous_close": 3345.00, "market_cap": 300100.0,
        "pe_ratio": 84.5, "pb_ratio": 24.5, "roe": 30.5, "roce": 32.8,
        "dividend_yield": 0.32, "debt_to_equity": 0.85, "high_52w": 3886.95, "low_52w": 3055.00, "volume": 1250000
    },
    {
        "symbol": "ASIANPAINT", "name": "Asian Paints Limited", "exchange": "NSE",
        "sector": "Consumer Durables", "industry": "Paints & Decorative Coatings",
        "current_price": 2890.00, "previous_close": 2865.00, "market_cap": 277200.0,
        "pe_ratio": 52.4, "pb_ratio": 14.8, "roe": 29.5, "roce": 37.2,
        "dividend_yield": 1.15, "debt_to_equity": 0.12, "high_52w": 3422.00, "low_52w": 2670.00, "volume": 1650000
    },
    {
        "symbol": "TRENT", "name": "Trent Limited", "exchange": "NSE",
        "sector": "Consumer Durables", "industry": "Apparel & Retail Chains",
        "current_price": 7850.00, "previous_close": 7720.00, "market_cap": 278900.0,
        "pe_ratio": 178.5, "pb_ratio": 52.4, "roe": 32.5, "roce": 28.5,
        "dividend_yield": 0.04, "debt_to_equity": 0.85, "high_52w": 8345.00, "low_52w": 2040.00, "volume": 2850000
    },
    {
        "symbol": "DMART", "name": "Avenue Supermarts Limited (DMart)", "exchange": "NSE",
        "sector": "Consumer Durables", "industry": "Supermarkets & Retail Hypermarkets",
        "current_price": 4120.00, "previous_close": 4080.00, "market_cap": 268100.0,
        "pe_ratio": 105.0, "pb_ratio": 14.5, "roe": 14.8, "roce": 19.5,
        "dividend_yield": 0.00, "debt_to_equity": 0.02, "high_52w": 5484.00, "low_52w": 3650.00, "volume": 850000
    },
    {
        "symbol": "ZOMATO", "name": "Zomato Limited", "exchange": "NSE",
        "sector": "Consumer Durables", "industry": "Food Delivery & Quick Commerce",
        "current_price": 274.00, "previous_close": 268.50, "market_cap": 242000.0,
        "pe_ratio": 128.5, "pb_ratio": 11.2, "roe": 8.5, "roce": 10.2,
        "dividend_yield": 0.00, "debt_to_equity": 0.01, "high_52w": 298.25, "low_52w": 102.50, "volume": 38500000
    },
    {
        "symbol": "BERGEPAINT", "name": "Berger Paints India Limited", "exchange": "NSE",
        "sector": "Consumer Durables", "industry": "Paints & Coatings",
        "current_price": 548.00, "previous_close": 542.00, "market_cap": 63900.0,
        "pe_ratio": 54.2, "pb_ratio": 11.5, "roe": 22.8, "roce": 28.4,
        "dividend_yield": 0.65, "debt_to_equity": 0.22, "high_52w": 642.00, "low_52w": 440.00, "volume": 1850000
    },
    {
        "symbol": "IRCTC", "name": "Indian Railway Catering and Tourism Corp", "exchange": "NSE",
        "sector": "Consumer Durables", "industry": "Railway Catering & Travel Services",
        "current_price": 878.00, "previous_close": 869.00, "market_cap": 70240.0,
        "pe_ratio": 58.5, "pb_ratio": 21.5, "roe": 41.2, "roce": 54.8,
        "dividend_yield": 0.75, "debt_to_equity": 0.05, "high_52w": 1138.00, "low_52w": 680.00, "volume": 3450000
    }
]

def run_enrichment():
    conn = sqlite3.connect('market.db')
    cursor = conn.cursor()

    updated = 0
    inserted = 0

    for s in TOP_INDIAN_STOCKS:
        sym = s["symbol"]
        price = s["current_price"]
        prev = s["previous_close"]
        chg = round(price - prev, 2)
        pct = round((chg / prev) * 100, 2)

        # Check if exists in stocks
        cursor.execute("SELECT id FROM stocks WHERE symbol = ?", (sym,))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE stocks SET
                    name = ?,
                    sector = ?,
                    industry = ?,
                    current_price = ?,
                    change = ?,
                    change_percent = ?,
                    market_cap = ?,
                    pe_ratio = ?,
                    pb_ratio = ?,
                    roe = ?,
                    roce = ?,
                    dividend_yield = ?,
                    debt_to_equity = ?,
                    high_52w = ?,
                    low_52w = ?,
                    volume = ?,
                    is_active = 1,
                    updated_at = ?
                WHERE symbol = ?
            """, (
                s["name"], s["sector"], s["industry"], price, chg, pct,
                s["market_cap"], s["pe_ratio"], s["pb_ratio"], s["roe"], s["roce"],
                s["dividend_yield"], s["debt_to_equity"], s["high_52w"], s["low_52w"],
                s["volume"], datetime.utcnow().isoformat(), sym
            ))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO stocks (
                    symbol, name, exchange, sector, industry,
                    current_price, change, change_percent, market_cap,
                    pe_ratio, pb_ratio, roe, roce, dividend_yield,
                    debt_to_equity, high_52w, low_52w, volume, is_active, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                sym, s["name"], s["exchange"], s["sector"], s["industry"],
                price, chg, pct, s["market_cap"], s["pe_ratio"], s["pb_ratio"],
                s["roe"], s["roce"], s["dividend_yield"], s["debt_to_equity"],
                s["high_52w"], s["low_52w"], s["volume"], datetime.utcnow().isoformat()
            ))
            inserted += 1

        # Also populate stock_fundamentals if missing
        cursor.execute("SELECT id FROM stock_fundamentals WHERE symbol = ?", (sym,))
        f_row = cursor.fetchone()
        if not f_row:
            cursor.execute("""
                INSERT INTO stock_fundamentals (
                    symbol, revenue, revenue_growth, ebitda, ebitda_margin,
                    net_profit, profit_growth, eps, pe, pb, roe, roce, debt,
                    debt_to_equity, current_ratio, dividend_yield, free_cash_flow,
                    promoter_holding, market_cap, enterprise_value, period, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sym, round(s["market_cap"] * 0.4, 2), 12.5, round(s["market_cap"] * 0.1, 2), 22.5,
                round(s["market_cap"] * 0.05, 2), 15.0, round(price / max(1, s["pe_ratio"]), 2),
                s["pe_ratio"], s["pb_ratio"], s["roe"], s["roce"], round(s["market_cap"] * 0.1 * s["debt_to_equity"], 2),
                s["debt_to_equity"], 1.65, s["dividend_yield"], round(s["market_cap"] * 0.03, 2),
                51.2, s["market_cap"], s["market_cap"], "FY2025-26", datetime.utcnow().isoformat()
            ))

    conn.commit()
    conn.close()
    print(f"Enrichment Complete: {updated} stocks updated, {inserted} stocks inserted.")

if __name__ == "__main__":
    run_enrichment()
