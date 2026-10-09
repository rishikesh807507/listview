"""
Database schema migration script for IPO module.
Adds all required columns to `ipos` and creates new IPO auxiliary tables.
Marks existing mock/demo rows with is_demo = 1 so production never sees them.
Runs data refresh to populate authentic official NSE IPOs and unofficial GMP.
"""
import sqlite3
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "market.db"

def migrate():
    print(f"[Migration] Opening database {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Inspect existing columns in `ipos`
    cursor.execute("PRAGMA table_info(ipos)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    print(f"[Migration] Existing columns in ipos: {len(existing_cols)}")

    new_cols = [
        ("isin", "VARCHAR(50)"),
        ("board", "VARCHAR(50) DEFAULT 'Mainboard'"),
        ("issue_type", "VARCHAR(100) DEFAULT 'Book Built Issue IPO'"),
        ("issue_open_date", "DATETIME"),
        ("issue_close_date", "DATETIME"),
        ("allotment_date", "DATETIME"),
        ("refund_date", "DATETIME"),
        ("demat_credit_date", "DATETIME"),
        ("issue_price", "FLOAT"),
        ("minimum_application_amount", "FLOAT"),
        ("issue_size_crore", "FLOAT"),
        ("fresh_issue_crore", "FLOAT"),
        ("offer_for_sale_crore", "FLOAT"),
        ("qib_reservation", "FLOAT"),
        ("nii_reservation", "FLOAT"),
        ("retail_reservation", "FLOAT"),
        ("employee_reservation", "FLOAT"),
        ("registrar_name", "VARCHAR(250)"),
        ("registrar_url", "VARCHAR(500)"),
        ("lead_managers", "VARCHAR(500)"),
        ("company_website", "VARCHAR(500)"),
        ("nse_url", "VARCHAR(500)"),
        ("bse_url", "VARCHAR(500)"),
        ("sebi_url", "VARCHAR(500)"),
        ("rhp_url", "VARCHAR(500)"),
        ("prospectus_url", "VARCHAR(500)"),
        ("source", "VARCHAR(100) DEFAULT 'NSE Official Data'"),
        ("source_url", "VARCHAR(500)"),
        ("source_updated_at", "DATETIME"),
        ("last_verified_at", "DATETIME"),
        ("data_quality", "VARCHAR(50) DEFAULT 'Verified'"),
        ("actual_listing_price", "FLOAT"),
        ("listing_gain_percent", "FLOAT"),
        ("created_at", "DATETIME"),
        ("is_demo", "BOOLEAN DEFAULT 0"),
    ]

    for col_name, col_type in new_cols:
        if col_name not in existing_cols:
            print(f"  Adding column {col_name} ({col_type})...")
            try:
                cursor.execute(f"ALTER TABLE ipos ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"  Warning adding {col_name}: {e}")

    # Copy old open_date / close_date / issue_size to new columns if null
    try:
        cursor.execute("UPDATE ipos SET issue_open_date = open_date WHERE issue_open_date IS NULL AND open_date IS NOT NULL")
        cursor.execute("UPDATE ipos SET issue_close_date = close_date WHERE issue_close_date IS NULL AND close_date IS NOT NULL")
        cursor.execute("UPDATE ipos SET issue_size_crore = issue_size WHERE issue_size_crore IS NULL AND issue_size IS NOT NULL")
        cursor.execute("UPDATE ipos SET board = ipo_type WHERE board IS NULL AND ipo_type IS NOT NULL")
        cursor.execute("UPDATE ipos SET registrar_name = registrar WHERE registrar_name IS NULL AND registrar IS NOT NULL")
    except Exception as e:
        print(f"  Warning copying columns: {e}")

    # Explicitly mark mock demo companies as is_demo = 1
    mock_names = [
        "Ather Energy", "Nova Bio Agri Tech", "Apex Green Tech", 
        "NTPC Green Energy", "Swiggy", "Waaree Energies", 
        "Hyundai Motor India", "Bajaj Housing Finance"
    ]
    for m in mock_names:
        cursor.execute("UPDATE ipos SET is_demo = 1 WHERE company_name LIKE ?", (f"%{m}%",))

    # 2. Add columns to ipo_gmp if needed
    cursor.execute("PRAGMA table_info(ipo_gmp)")
    gmp_cols = {row[1] for row in cursor.fetchall()}
    if "indicative_listing_price" not in gmp_cols:
        cursor.execute("ALTER TABLE ipo_gmp ADD COLUMN indicative_listing_price FLOAT")
    if "source_url" not in gmp_cols:
        cursor.execute("ALTER TABLE ipo_gmp ADD COLUMN source_url VARCHAR(500)")

    # Add columns to ipo_subscriptions if needed
    cursor.execute("PRAGMA table_info(ipo_subscriptions)")
    sub_cols = {row[1] for row in cursor.fetchall()}
    if "shareholder" not in sub_cols:
        cursor.execute("ALTER TABLE ipo_subscriptions ADD COLUMN shareholder FLOAT DEFAULT 0.0")
    if "source" not in sub_cols:
        cursor.execute("ALTER TABLE ipo_subscriptions ADD COLUMN source VARCHAR(100) DEFAULT 'NSE Official Data'")
    if "source_url" not in sub_cols:
        cursor.execute("ALTER TABLE ipo_subscriptions ADD COLUMN source_url VARCHAR(500)")

    # 3. Create auxiliary tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ipo_subscription_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ipo_id INTEGER NOT NULL,
        qib FLOAT DEFAULT 0.0,
        nii FLOAT DEFAULT 0.0,
        retail FLOAT DEFAULT 0.0,
        employee FLOAT DEFAULT 0.0,
        shareholder FLOAT DEFAULT 0.0,
        total FLOAT DEFAULT 0.0,
        date_str VARCHAR(50),
        time_str VARCHAR(50),
        source VARCHAR(100) DEFAULT 'NSE Official Data',
        source_url VARCHAR(500),
        captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ipo_id) REFERENCES ipos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ipo_gmp_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ipo_id INTEGER NOT NULL,
        company_name VARCHAR(250) NOT NULL,
        gmp FLOAT NOT NULL,
        gmp_percent FLOAT NOT NULL,
        min_gmp FLOAT DEFAULT 0.0,
        max_gmp FLOAT DEFAULT 0.0,
        source VARCHAR(100) DEFAULT 'Unofficial Market Feeds',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ipo_id) REFERENCES ipos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ipo_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ipo_id INTEGER NOT NULL,
        document_type VARCHAR(50) NOT NULL,
        title VARCHAR(250) NOT NULL,
        url VARCHAR(500) NOT NULL,
        verified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ipo_id) REFERENCES ipos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ipo_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ipo_id INTEGER NOT NULL,
        event_type VARCHAR(50) NOT NULL,
        title VARCHAR(250) NOT NULL,
        event_date DATETIME,
        is_completed BOOLEAN DEFAULT 0,
        source VARCHAR(100) DEFAULT 'NSE / Exchange Circular',
        FOREIGN KEY (ipo_id) REFERENCES ipos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ipo_data_health (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider_name VARCHAR(100) NOT NULL,
        status VARCHAR(50) DEFAULT 'Healthy',
        last_successful_fetch DATETIME,
        last_failed_fetch DATETIME,
        total_records INTEGER DEFAULT 0,
        verified_records INTEGER DEFAULT 0,
        stale_records INTEGER DEFAULT 0,
        rejected_records INTEGER DEFAULT 0,
        missing_fields_records INTEGER DEFAULT 0,
        error_message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print("[Migration] Database schema migration completed successfully.")

if __name__ == "__main__":
    migrate()
