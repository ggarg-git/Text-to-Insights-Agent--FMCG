import os
from openai import OpenAI

# Initialize the OpenAI client. It automatically searches for the OPENAI_API_KEY environment variable.
client = OpenAI()

# -------------------------------------------------------------------
# THE SEMANTIC LAYER / DATABASE CONTEXT
# -------------------------------------------------------------------
# This context is appended to every prompt so the LLM maps business terms to exact column schema rules.
FMCG_SCHEMA_CONTEXT = """
Table Name: fmcg_media_performance
Columns:
- date (TEXT, format YYYY-MM-DD)
- brand (TEXT, e.g., 'EcoSoap')
- platform (TEXT, e.g., 'Amazon Advertising', 'Meta (Insta/FB)', 'Google Search', 'TikTok', 'Instacart Ads')
- campaign_type (TEXT, e.g., 'Sponsored Products', 'Prospecting Video', 'Brand Terms', 'Retargeting DPA')
- spend (REAL, budget spent in USD)
- impressions (INTEGER, upper funnel views)
- clicks (INTEGER, traffic driver)
- add_to_carts (INTEGER, mid-funnel purchase intent marker)
- purchases (INTEGER, bottom funnel conversion count)
- revenue (REAL, gross sales revenue generated in USD)

Calculated Business Metrics Formulations:
- ROAS (Return on Ad Spend) = SUM(revenue) / SUM(spend)
- CAC / CPA (Cost Per Acquisition) = SUM(spend) / SUM(purchases)
- CPC (Cost Per Click) = SUM(spend) / SUM(clicks)
- Cart-to-Purchase Conversion Rate = SUM(purchases) / SUM(add_to_carts)
- CTR (Click-Through Rate) = SUM(clicks) / SUM(impressions)
"""

def text_to_sql_agent(user_query: str) -> str:
    """
    Agent Layer 1: Interprets business user intent and translates it 
    into a precise, syntactically correct SQLite query.
    """
    system_prompt = f"""
    You are an expert Data Scientist and Analytics Engineer specialized in FMCG/CPG Digital Media Performance.
    Your sole task is to write a clean, optimized SQLite query based on the user's question.
    
    Database Schema Context:
    {FMCG_SCHEMA_CONTEXT}
    
    CRITICAL RULES:
    1. Return ONLY the raw SQL query string. Do not wrap it in markdown blocks like ```sql ... ```. No explanations.
    2. Protect against division by zero errors by ensuring denominators are checked or conditional.
    3. Use standard SQL aggregations (SUM, AVG) where appropriate.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Using a highly efficient reasoning model for structured tasks
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0.0  # Force maximum determinism for reliable code generation
    )
    return response.choices[0].message.content.strip()

def presentation_agent(user_query: str, sql_used: str, dataframe_result) -> str:
    """
    Agent Layer 2: Post-processes the raw Pandas dataframe into a clean business presentation.
    """
    # Convert dataframe to a native markdown layout
    markdown_table = dataframe_result.to_markdown(index=False, tablefmt="github")
    
    system_prompt = """
    You are a Director of Growth Marketing. Present raw data table results to executive brand managers.
    
    RULES:
    1. Output the provided table data cleanly. Ensure currency metrics contain '$' headers/symbols and clean up decimal precision.
    2. Provide exactly two high-impact, bulleted business takeaways highlighting efficiency, scale, or channel bottlenecks. Do not hallucinate numbers.
    """
    
    content_payload = f"""
    User Question: {user_query}
    SQL Executed: {sql_used}
    Raw Data Table:
    {markdown_table}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_payload}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content
