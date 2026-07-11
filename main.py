# main.py
import os
import sys
from src.db_engine import get_db_connection, initialize_fmcg_warehouse, run_read_query
from src.agent_core import text_to_sql_agent, presentation_agent

def run_analytics_agent(business_question: str):
    print(f"📋 Business User Query: '{business_question}'")
    print("-" * 60)
    
    # 1. Initialize data layer connection
    conn = get_db_connection()
    initialize_fmcg_warehouse(conn)
    
    try:
        # 2. Run the Text-to-SQL Agent Translation
        generated_sql = text_to_sql_agent(business_question)
        print(f"💻 Agent Generated SQL:\n{generated_sql}\n")
        
        # 3. Execute query securely through database module guardrails
        raw_df = run_read_query(generated_sql, conn)
        
        # 4. Format and deliver consumer insights
        final_report = presentation_agent(business_question, generated_sql, raw_df)
        print("📊 Beautiful Business View Rendered:")
        print("=" * 60)
        print(final_report)
        print("=" * 60)
        
    except Exception as e:
        print(f"🚨 Pipeline Error: {e}", file=sys.stderr)
    finally:
        conn.close()

if __name__ == "__main__":
    # Test sample business query asking for calculated metrics
    sample_query = "Which media platforms are giving us a ROAS above 2.0? Show total spend, total revenue, and calculated ROAS."
    run_analytics_agent(sample_query)
