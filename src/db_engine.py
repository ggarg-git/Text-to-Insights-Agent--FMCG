import sqlite3
import pandas as pd

def get_db_connection():
    """Establishes an in-memory database connection mimicking a data warehouse connection."""
    # In production, this would use sqlalchemy.create_engine() for Snowflake/BigQuery
    return sqlite3.connect(":memory:")

def initialize_fmcg_warehouse(conn):
    """Creates the structural tables and hydrates them with mock performance log entries."""
    cursor = conn.cursor()
    
    # 1. Create Schema
    cursor.execute("""
        CREATE TABLE fmcg_media_performance (
            date TEXT,
            brand TEXT,
            platform TEXT,
            campaign_type TEXT,
            spend REAL,
            impressions INTEGER,
            clicks INTEGER,
            add_to_carts INTEGER,
            purchases INTEGER,
            revenue REAL
        )
    """)
    
    # 2. Seed Mock FMCG Funnel Data
    mock_logs = [
        ("2026-07-01", "EcoSoap", "Amazon Advertising", "Sponsored Products", 1200.0, 80000, 2400, 480, 160, 4800.0),
        ("2026-07-01", "EcoSoap", "Meta (Insta/FB)", "Prospecting Video", 3500.0, 450000, 9000, 310, 85, 2550.0),
        ("2026-07-01", "EcoSoap", "Google Search", "Brand Terms", 800.0, 12000, 1800, 400, 210, 6300.0),
        ("2026-07-02", "EcoSoap", "Amazon Advertising", "Sponsored Brands", 1500.0, 95000, 1900, 380, 110, 3300.0),
        ("2026-07-02", "EcoSoap", "TikTok", "Influencer Spark", 2800.0, 600000, 14000, 520, 90, 2700.0),
        ("2026-07-02", "EcoSoap", "Instacart Ads", "Category Search", 900.0, 25000, 1500, 450, 190, 3800.0),
        ("2026-07-03", "EcoSoap", "Meta (Insta/FB)", "Retargeting DPA", 1800.0, 120000, 4000, 610, 220, 6600.0)
    ]
    
    cursor.executemany("INSERT INTO fmcg_media_performance VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", mock_logs)
    conn.commit()

def run_read_query(sql_query: str, conn) -> pd.DataFrame:
    """
    Executes an incoming query string securely. 
    Intercepts and blocks destructive write actions.
    """
    # Defensive programming guardrail
    sanitized_query = sql_query.strip().lower()
    destructive_keywords = ["drop", "delete", "truncate", "update", "insert", "alter", "grant"]
    
    if any(keyword in sanitized_query for keyword in destructive_keywords):
        raise PermissionError("Security Breach Blocked: Destructive database modifications are prohibited.")
    
    # Execute query cleanly into a Pandas DataFrame
    return pd.read_sql_query(sql_query, conn)
