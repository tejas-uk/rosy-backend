#!/usr/bin/env python3
"""Production initialization script for Render deployment."""

import os
import sys
from dotenv import load_dotenv
import psycopg

# Load environment variables
load_dotenv()

def init_production_db():
    """Initialize database tables for production."""
    conn_string = os.getenv("SUPABASE_URL")
    if not conn_string:
        print("❌ SUPABASE_URL environment variable not set")
        sys.exit(1)
    
    try:
        print("🔄 Connecting to production database...")
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("📋 Creating lily_users table...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS lily_users (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(64) NOT NULL,
                        email VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                print("📋 Creating chat_threads table...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_threads (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        thread_id VARCHAR(100) UNIQUE NOT NULL,
                        user_id UUID REFERENCES lily_users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                print("✅ Production database initialized successfully!")
                
    except Exception as e:
        print(f"❌ Error initializing production database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_production_db()