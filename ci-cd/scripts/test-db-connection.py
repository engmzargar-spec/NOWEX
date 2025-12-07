#!/usr/bin/env python3
"""
Test database connection script.
This script tests the database connection for CI/CD pipelines.
"""

import sys
import os
import psycopg2
from psycopg2 import OperationalError
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_postgres_connection(host='localhost', port=5432, database='novex_test', 
                            user='postgres', password='postgres'):
    """Test PostgreSQL connection."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        
        logger.info(f"✅ PostgreSQL Connection Successful")
        logger.info(f"   Database: {db_name}")
        logger.info(f"   Version: {version.split(',')[0]}")
        
        # Test basic operations
        cursor.execute("SELECT 1 + 1 as result")
        result = cursor.fetchone()[0]
        logger.info(f"   Test calculation: 1 + 1 = {result}")
        
        cursor.close()
        conn.close()
        return True
        
    except OperationalError as e:
        logger.error(f"❌ PostgreSQL Connection Failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def test_redis_connection(host='localhost', port=6379):
    """Test Redis connection."""
    try:
        import redis
        r = redis.Redis(host=host, port=port, socket_connect_timeout=5)
        
        # Test connection
        r.ping()
        logger.info(f"✅ Redis Connection Successful")
        
        # Test set/get
        test_key = "ci_cd_test"
        test_value = "connection_test"
        r.set(test_key, test_value, ex=10)
        retrieved = r.get(test_key)
        
        if retrieved.decode() == test_value:
            logger.info(f"   Redis set/get test passed")
        else:
            logger.warning(f"   Redis set/get test failed")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Redis Connection Failed: {e}")
        return False

def main():
    """Main function."""
    logger.info("Starting database connection tests...")
    
    # Get connection details from environment variables
    pg_host = os.getenv('POSTGRES_HOST', 'localhost')
    pg_port = int(os.getenv('POSTGRES_PORT', '5432'))
    pg_db = os.getenv('POSTGRES_DB', 'novex_test')
    pg_user = os.getenv('POSTGRES_USER', 'postgres')
    pg_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', '6379'))
    
    # Run tests
    pg_success = test_postgres_connection(
        host=pg_host,
        port=pg_port,
        database=pg_db,
        user=pg_user,
        password=pg_password
    )
    
    redis_success = test_redis_connection(
        host=redis_host,
        port=redis_port
    )
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY:")
    logger.info(f"  PostgreSQL: {'✅ PASS' if pg_success else '❌ FAIL'}")
    logger.info(f"  Redis: {'✅ PASS' if redis_success else '❌ FAIL'}")
    logger.info("="*50)
    
    # Exit code
    if pg_success and redis_success:
        logger.info("All tests passed! ✅")
        sys.exit(0)
    else:
        logger.error("Some tests failed! ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()
