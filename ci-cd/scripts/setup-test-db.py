#!/usr/bin/env python3
"""
Setup test database for CI/CD pipelines.
Creates test database, tables, and seed data.
"""

import sys
import os
import psycopg2
from psycopg2 import sql
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database(conn_params, db_name):
    """Create test database if it doesn't exist."""
    try:
        # Connect to default postgres database to create new database
        conn_params['database'] = 'postgres'
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        
        if cursor.fetchone():
            logger.info(f"Database '{db_name}' already exists")
        else:
            # Create database
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            ))
            logger.info(f"✅ Created database '{db_name}'")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create database: {e}")
        return False

def run_sql_file(conn, filepath):
    """Run SQL commands from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor = conn.cursor()
        
        # Split by semicolon and execute each command
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        for command in commands:
            if command:  # Skip empty commands
                cursor.execute(command)
        
        conn.commit()
        cursor.close()
        logger.info(f"✅ Executed SQL file: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to execute SQL file {filepath}: {e}")
        conn.rollback()
        return False

def setup_database_structure(conn):
    """Setup database tables and structure."""
    try:
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if existing_tables:
            logger.info(f"Found {len(existing_tables)} existing tables")
            # Drop all tables for clean test environment
            if os.getenv('CLEAN_DB', 'false').lower() == 'true':
                logger.info("Cleaning database (dropping all tables)...")
                for table in existing_tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                conn.commit()
                logger.info("✅ Database cleaned")
        
        # Run migration files
        migrations_dir = "database/migrations"
        if os.path.exists(migrations_dir):
            migration_files = sorted([
                f for f in os.listdir(migrations_dir) 
                if f.endswith('.sql') and not f.startswith('.')
            ])
            
            for migration_file in migration_files:
                migration_path = os.path.join(migrations_dir, migration_file)
                if not run_sql_file(conn, migration_path):
                    return False
        else:
            logger.warning(f"Migrations directory not found: {migrations_dir}")
        
        cursor.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup database structure: {e}")
        return False

def seed_test_data(conn):
    """Seed database with test data."""
    try:
        cursor = conn.cursor()
        
        # Check if we need to seed data
        cursor.execute("SELECT COUNT(*) FROM users LIMIT 1")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            logger.info(f"Database already has {user_count} users, skipping seed")
            cursor.close()
            return True
        
        # Run seed files
        seeds_dir = "database/seeds"
        if os.path.exists(seeds_dir):
            seed_files = [
                "seed_data.sql",
                "test_users.sql",
                "admin_seed.sql",
                "scoring_levels_seed.sql",
                "kyc_seed_data.sql"
            ]
            
            for seed_file in seed_files:
                seed_path = os.path.join(seeds_dir, seed_file)
                if os.path.exists(seed_path):
                    if not run_sql_file(conn, seed_path):
                        logger.warning(f"Failed to seed: {seed_file}")
                else:
                    logger.info(f"Seed file not found: {seed_path}")
        else:
            logger.warning(f"Seeds directory not found: {seeds_dir}")
        
        # Create test admin user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, is_active, is_admin)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, (
            'test_admin',
            'admin@test.novex',
            '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # 'testpass'
            True,
            True
        ))
        
        # Create test regular user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, is_active, is_admin)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, (
            'test_user',
            'user@test.novex',
            '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # 'testpass'
            True,
            False
        ))
        
        conn.commit()
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM kyc_profiles")
        kyc_count = cursor.fetchone()[0]
        
        logger.info(f"✅ Seeded test data:")
        logger.info(f"   Users: {user_count}")
        logger.info(f"   KYC Profiles: {kyc_count}")
        
        cursor.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to seed test data: {e}")
        conn.rollback()
        return False

def main():
    """Main function."""
    logger.info("Setting up test database...")
    
    # Connection parameters
    conn_params = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    }
    
    db_name = os.getenv('POSTGRES_DB', 'novex_test')
    
    # Step 1: Create database
    if not create_database(conn_params, db_name):
        sys.exit(1)
    
    # Step 2: Connect to the new database
    conn_params['database'] = db_name
    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = False
    except Exception as e:
        logger.error(f"❌ Failed to connect to database '{db_name}': {e}")
        sys.exit(1)
    
    # Step 3: Setup database structure
    if not setup_database_structure(conn):
        conn.close()
        sys.exit(1)
    
    # Step 4: Seed test data
    if not seed_test_data(conn):
        conn.close()
        sys.exit(1)
    
    # Final validation
    try:
        cursor = conn.cursor()
        
        # Check essential tables
        essential_tables = ['users', 'kyc_profiles', 'scores', 'referrals']
        for table in essential_tables:
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (table,))
            exists = cursor.fetchone()[0]
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"   {table}: {count} records")
            else:
                logger.warning(f"   {table}: NOT FOUND")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Final validation failed: {e}")
        conn.close()
        sys.exit(1)
    
    logger.info("="*50)
    logger.info("✅ Test database setup completed successfully!")
    logger.info("="*50)
    sys.exit(0)

if __name__ == "__main__":
    main()
