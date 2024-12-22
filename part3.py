import json
from supabase import create_client, Client
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def execute_function(function_name, params=None):
    if params is None:
        params = {}    
    try:
        response = supabase.rpc(function_name, params).execute()
        return response.data
    except Exception as e:
        print(f"Error executing function {function_name}: {e}")
        return None
    

def store_insights(average_ctr, top_queries, low_performance_queries):
    insight_date = datetime.now().date()

    top_queries_json = json.dumps(top_queries)
    low_performance_queries_json = json.dumps(low_performance_queries)

    try:
        response = supabase.table("search_insights").insert({
            "insight_date": str(insight_date),
            "average_ctr": average_ctr,
            "top_queries": top_queries_json,
            "low_performance_queries": low_performance_queries_json
        }).execute()
        return response
    except Exception as e:
        print(f"Error inserting data: {e}")
        return None

def run_pipeline():
    average_ctr_data = execute_function("get_average_ctr")
    top_queries_data = execute_function("get_top_queries", {"start_date": "2024-01-01", "end_date": "2024-12-31"})
    low_performance_queries_data = execute_function("get_low_performance_queries")

    if average_ctr_data is None or top_queries_data is None or low_performance_queries_data is None:
        print("One of the functions did not return data. Exiting.")
        return

    average_ctr = sum([item['average_ctr'] for item in average_ctr_data]) / len(average_ctr_data) if average_ctr_data else 0

    store_insights(average_ctr, top_queries_data, low_performance_queries_data)

run_pipeline()