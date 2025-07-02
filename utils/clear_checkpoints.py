#!/usr/bin/env python3
"""Clear PostgreSQL checkpointer data when message schemas change."""

from dotenv import load_dotenv
import os
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

load_dotenv(dotenv_path="../.env", override=True)

def clear_checkpoints():
    """Clear all checkpoint data from PostgreSQL."""
    if os.getenv("CHECKPOINTER") == "postgres":
        conn_string = os.getenv("SUPABASE_URL")
        print(f"Connecting to: {conn_string}")
        
        try:
            with psycopg.connect(conn_string) as conn:
                with conn.cursor() as cur:
                    # List all tables first
                    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
                    tables = cur.fetchall()
                    print(f"Available tables: {[t[0] for t in tables]}")
                    
                    # Check if checkpoint tables exist and clear them
                    for table_name in ['checkpoints', 'checkpoint_blobs', 'checkpoint_writes']:
                        try:
                            cur.execute(f"TRUNCATE TABLE {table_name} CASCADE")
                            print(f"Cleared table: {table_name}")
                        except Exception as table_error:
                            print(f"Could not clear {table_name}: {table_error}")
                    
                    # Also try to delete specific records
                    try:
                        cur.execute("DELETE FROM checkpoints")
                        cur.execute("DELETE FROM checkpoint_blobs") 
                        cur.execute("DELETE FROM checkpoint_writes")
                        print("Deleted all records from checkpoint tables")
                    except Exception as delete_error:
                        print(f"Could not delete records: {delete_error}")
                    
                    conn.commit()
                    print("✅ Successfully cleared all checkpoint data")
        except Exception as e:
            print(f"❌ Error clearing checkpoints: {e}")
    else:
        print("Not using PostgreSQL checkpointer - nothing to clear")

if __name__ == "__main__":
    clear_checkpoints()