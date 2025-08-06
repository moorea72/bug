#!/usr/bin/env python3
"""
Test Neon PostgreSQL connection
"""
import os
import sqlalchemy
from sqlalchemy import create_engine, text

def test_neon_connection():
    """Test connection to Neon PostgreSQL database"""
    
    database_url = "postgresql://neondb_owner:npg_4sSItw5JkLZM@ep-falling-firefly-afxbamco-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    try:
        print("Testing Neon PostgreSQL connection...")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✓ Connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Test table creation
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert test data
            connection.execute(text("""
                INSERT INTO test_table (name) VALUES ('Test Entry')
                ON CONFLICT DO NOTHING
            """))
            
            # Read test data
            result = connection.execute(text("SELECT * FROM test_table LIMIT 1"))
            row = result.fetchone()
            if row:
                print(f"✓ Test data: ID={row[0]}, Name={row[1]}")
            
            # Clean up
            connection.execute(text("DROP TABLE IF EXISTS test_table"))
            connection.commit()
            
            print("✓ Neon PostgreSQL database is ready!")
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_neon_connection()
    if success:
        print("\n🎉 Neon PostgreSQL integration successful!")
    else:
        print("\n❌ Neon PostgreSQL integration failed!")