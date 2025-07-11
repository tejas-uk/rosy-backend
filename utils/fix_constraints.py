#!/usr/bin/env python3
"""Fix database constraints."""

from dotenv import load_dotenv
import os
import psycopg

load_dotenv(dotenv_path=".env", override=True)

def fix_constraints():
    """Fix database foreign key constraints."""
    conn_string = os.getenv("SUPABASE_URL")
    if not conn_string:
        print("❌ SUPABASE_URL not configured")
        return
    
    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("Fixing database constraints...")
                
                # Create simple_users table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS simple_users (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        username VARCHAR(50) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Ensured simple_users table exists")
                
                # Drop and recreate chat_threads table with correct constraints
                cur.execute("DROP TABLE IF EXISTS chat_threads CASCADE")
                print("✅ Dropped old chat_threads table")
                
                cur.execute("""
                    CREATE TABLE chat_threads (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        thread_id VARCHAR(100) UNIQUE NOT NULL,
                        user_id UUID REFERENCES lily_users(id) ON DELETE CASCADE,
                        simple_user_id UUID REFERENCES simple_users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Created new chat_threads table with correct constraints")
                
                conn.commit()
                print("🎉 Database constraints fixed!")
                
    except Exception as e:
        print(f"❌ Error fixing constraints: {e}")

if __name__ == "__main__":
    fix_constraints()