#!/usr/bin/env python3
"""
Check essential API endpoints for CI/CD pipelines.
Verifies that critical endpoints are accessible and returning correct status codes.
"""

import sys
import os
import requests
import json
import time
import logging
from typing import List, Dict, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EndpointChecker:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NOWEX-CI-CD/1.0',
            'Accept': 'application/json'
        })
        
    def check_endpoint(self, endpoint: str, method: str = 'GET', 
                      expected_status: int = 200, **kwargs) -> Tuple[bool, Dict]:
        """
        Check a single endpoint.
        
        Returns: (success, response_data)
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response_time = time.time() - start_time
            
            success = response.status_code == expected_status
            
            result = {
                'url': url,
                'method': method,
                'expected_status': expected_status,
                'actual_status': response.status_code,
                'response_time': round(response_time, 3),
                'success': success,
                'size': len(response.content) if response.content else 0
            }
            
            if success:
                logger.info(f"✅ {method} {endpoint}: {response.status_code} ({response_time:.3f}s)")
            else:
                logger.error(f"❌ {method} {endpoint}: Expected {expected_status}, got {response.status_code}")
                
                # Try to get error details
                try:
                    error_data = response.json()
                    logger.error(f"   Error: {error_data}")
                except:
                    logger.error(f"   Response: {response.text[:200]}")
            
            return success, result
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ {method} {endpoint}: Timeout after {self.timeout}s")
            return False, {
                'url': url,
                'method': method,
                'error': 'timeout',
                'success': False
            }
            
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ {method} {endpoint}: Connection error")
            return False, {
                'url': url,
                'method': method,
                'error': 'connection_error',
                'success': False
            }
            
        except Exception as e:
            logger.error(f"❌ {method} {endpoint}: Unexpected error: {e}")
            return False, {
                'url': url,
                'method': method,
                'error': str(e),
                'success': False
            }
    
    def check_health_endpoint(self) -> bool:
        """Check health endpoint."""
        success, result = self.check_endpoint('/api/health', expected_status=200)
        
        if success and result.get('size', 0) > 0:
            try:
                response = self.session.get(f"{self.base_url}/api/health", timeout=self.timeout)
                health_data = response.json()
                
                # Check health status
                if health_data.get('status') == 'healthy':
                    logger.info(f"✅ Health status: {health_data.get('status')}")
                    
                    # Log additional health info
                    if 'timestamp' in health_data:
                        logger.info(f"   Timestamp: {health_data['timestamp']}")
                    if 'version' in health_data:
                        logger.info(f"   Version: {health_data['version']}")
                        
                    return True
                else:
                    logger.error(f"❌ Health status not 'healthy': {health_data.get('status')}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Failed to parse health response: {e}")
                return False
        
        return success
    
    def check_openapi_docs(self) -> bool:
        """Check OpenAPI/Swagger documentation."""
        endpoints_to_check = [
            ('/docs', 200),  # Swagger UI
            ('/redoc', 200),  # ReDoc
            ('/openapi.json', 200),  # OpenAPI JSON
        ]
        
        all_success = True
        for endpoint, expected_status in endpoints_to_check:
            success, _ = self.check_endpoint(endpoint, expected_status=expected_status)
            if not success:
                all_success = False
        
        return all_success
    
    def check_authentication_endpoints(self) -> bool:
        """Check authentication related endpoints."""
        endpoints = [
            ('/api/auth/login', 'POST', 401),  # Should return 401 without credentials
            ('/api/auth/register', 'POST', 400),  # Should return 400 without data
            ('/api/auth/refresh', 'POST', 401),  # Should return 401 without token
        ]
        
        all_success = True
        for endpoint, method, expected_status in endpoints:
            success, _ = self.check_endpoint(
                endpoint, 
                method=method, 
                expected_status=expected_status,
                json={}  # Empty JSON payload
            )
            if not success:
                all_success = False
        
        return all_success
    
    def check_business_endpoints(self) -> bool:
        """Check business logic endpoints."""
        endpoints = [
            ('/api/kyc/status', 'GET', 401),  # Needs authentication
            ('/api/scoring/score', 'GET', 401),  # Needs authentication
            ('/api/finance/balance', 'GET', 401),  # Needs authentication
            ('/api/referral/stats', 'GET', 401),  # Needs authentication
        ]
        
        all_success = True
        for endpoint, method, expected_status in endpoints:
            success, _ = self.check_endpoint(
                endpoint, 
                method=method, 
                expected_status=expected_status
            )
            if not success:
                all_success = False
        
        return all_success
    
    def check_admin_endpoints(self) -> bool:
        """Check admin endpoints (should return 401/403 without admin auth)."""
        endpoints = [
            ('/api/admin/users', 'GET', 401),
            ('/api/admin/kyc/pending', 'GET', 401),
        ]
        
        all_success = True
        for endpoint, method, expected_status in endpoints:
            success, _ = self.check_endpoint(
                endpoint, 
                method=method, 
                expected_status=expected_status
            )
            if not success:
                all_success = False
        
        return all_success

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check essential API endpoints')
    parser.add_argument('--base-url', default='http://localhost:8000',
                       help='Base URL of the API (default: http://localhost:8000)')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')
    parser.add_argument('--endpoints', nargs='+',
                       default=['health', 'docs', 'auth', 'business', 'admin'],
                       help='Endpoints to check (default: all)')
    
    args = parser.parse_args()
    
    logger.info(f"Checking essential endpoints for: {args.base_url}")
    logger.info(f"Timeout: {args.timeout}s")
    logger.info(f"Endpoints to check: {args.endpoints}")
    logger.info("="*60)
    
    checker = EndpointChecker(args.base_url, args.timeout)
    results = {}
    
    # Health check
    if 'health' in args.endpoints:
        logger.info("\n1. Health Check:")
        results['health'] = checker.check_health_endpoint()
    
    # Documentation check
    if 'docs' in args.endpoints:
        logger.info("\n2. Documentation Check:")
        results['docs'] = checker.check_openapi_docs()
    
    # Authentication endpoints
    if 'auth' in args.endpoints:
        logger.info("\n3. Authentication Endpoints:")
        results['auth'] = checker.check_authentication_endpoints()
    
    # Business endpoints
    if 'business' in args.endpoints:
        logger.info("\n4. Business Endpoints:")
        results['business'] = checker.check_business_endpoints()
    
    # Admin endpoints
    if 'admin' in args.endpoints:
        logger.info("\n5. Admin Endpoints:")
        results['admin'] = checker.check_admin_endpoints()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("CHECK SUMMARY:")
    
    total_checks = len(results)
    passed_checks = sum(1 for success in results.values() if success)
    
    for check_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {check_name}: {status}")
    
    logger.info("="*60)
    logger.info(f"TOTAL: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        logger.info("✅ All essential endpoints are accessible!")
        sys.exit(0)
    else:
        logger.error(f"❌ {total_checks - passed_checks} checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
