#!/usr/bin/env python3
"""
Test Azure API Endpoints

This script tests the various API endpoints on the Azure-hosted backend
to diagnose connectivity and functionality issues.
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Azure backend URL
AZURE_URL = "https://sarada-hbegajbsfxekdyex.canadacentral-01.azurewebsites.net"

def test_endpoint(endpoint, method="GET", data=None, print_response=True):
    """Test a specific API endpoint and print the results."""
    url = urljoin(AZURE_URL, endpoint)
    print(f"\n=== Testing {method} {url} ===")
    
    headers = {"Content-Type": "application/json"}
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            print(f"Unsupported method: {method}")
            return False
            
        print(f"Status Code: {response.status_code}")
        print(f"Status Message: {response.reason}")
        
        # Try to parse JSON response if available
        if print_response:
            try:
                json_response = response.json()
                print("Response:")
                print(json.dumps(json_response, indent=2))
            except:
                print("Raw Response:")
                print(response.text[:500] + ("..." if len(response.text) > 500 else ""))
        
        # Return True if successful (2xx status code)
        return 200 <= response.status_code < 300
        
    except requests.RequestException as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print(f"Testing Azure backend at: {AZURE_URL}")
    
    # Test health endpoint
    health_ok = test_endpoint("/api/health")
    
    # Test posts endpoint
    posts_ok = test_endpoint("/api/posts")
    
    # Test login endpoint with dummy credentials (to check if endpoint exists)
    login_data = {"username": "test_user_not_real", "password": "wrong_password"}
    login_ok = test_endpoint("/api/login", method="POST", data=login_data)
    
    # Try admin login with our created admin credentials
    admin_login_data = {"username": "admin", "password": "secure_password123"}
    admin_login_ok = test_endpoint("/api/login", method="POST", data=admin_login_data)
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Health Endpoint: {'✅ OK' if health_ok else '❌ Failed'}")
    print(f"Posts Endpoint:  {'✅ OK' if posts_ok else '❌ Failed'}")
    print(f"Login Endpoint:  {'✅ OK' if login_ok else '❌ Failed'}")
    print(f"Admin Login:     {'✅ OK' if admin_login_ok else '❌ Failed'}")
    
    # Detailed recommendations based on results
    print("\n=== Recommendations ===")
    if not health_ok:
        print("❌ Backend is not running or not accessible. Check deployment and Azure App Service status.")
    elif not posts_ok:
        print("❌ The '/api/posts' endpoint is not working. Check server logs for errors.")
        print("   Possible issues:")
        print("   - Database not properly initialized or missing tables")
        print("   - Route not correctly defined in app.py")
        print("   - Error in SQL query execution")
    elif not login_ok and not admin_login_ok:
        print("❌ Authentication endpoints not working. Check server logs.")
    elif not admin_login_ok:
        print("❌ Admin login failed. The admin account might not be properly created.")
    else:
        print("✅ All endpoints working correctly!")

if __name__ == "__main__":
    main() 