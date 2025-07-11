#!/usr/bin/env python3
"""Initialize database tables for Lily API."""

from dotenv import load_dotenv
import os
import psycopg

load_dotenv(dotenv_path=".env", override=True)

def init_database():
    """Initialize all required database tables."""
    conn_string = os.getenv("SUPABASE_URL")
    if not conn_string:
        print("❌ SUPABASE_URL not configured")
        return
    
    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("Creating database tables...")
                
                # Create lily_users table (avoid conflict with Supabase auth.users)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS lily_users (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(64) NOT NULL,
                        email VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Created lily_users table")
                
                # Create simple_users table for username-only authentication
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS simple_users (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        username VARCHAR(50) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Created simple_users table")
                
                # Create chat_threads table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_threads (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        thread_id VARCHAR(100) UNIQUE NOT NULL,
                        user_id UUID REFERENCES lily_users(id) ON DELETE CASCADE,
                        simple_user_id UUID REFERENCES simple_users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Created chat_threads table")
                
                conn.commit()
                print("🎉 Database initialization complete!")
                
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

if __name__ == "__main__":
    init_database()