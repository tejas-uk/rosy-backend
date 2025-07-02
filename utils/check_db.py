#!/usr/bin/env python3
"""Check database structure."""

from dotenv import load_dotenv
import os
import psycopg

load_dotenv(dotenv_path=".env", override=True)

def check_database():
    """Check database structure."""
    conn_string = os.getenv("SUPABASE_URL")
    if not conn_string:
        print("❌ SUPABASE_URL not configured")
        return
    
    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # List all tables
                cur.execute("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """)
                tables = cur.fetchall()
                print("📋 Available tables:")
                for table in tables:
                    print(f"  - {table[0]}")
                
                # Check users table structure if it exists
                try:
                    cur.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'users'
                        ORDER BY ordinal_position
                    """)
                    columns = cur.fetchall()
                    if columns:
                        print("\n👤 Users table structure:")
                        for col in columns:
                            print(f"  - {col[0]}: {col[1]}")
                    else:
                        print("\n❌ Users table not found or has no columns")
                except Exception as e:
                    print(f"\n❌ Error checking users table: {e}")
                
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

if __name__ == "__main__":
    check_database()