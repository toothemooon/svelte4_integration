#!/usr/bin/env python3
"""
Comprehensive Test for Azure API Routes

This script tests various URL formats and paths to diagnose Azure routing issues.
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Azure backend URL (base version)
AZURE_URL = "https://sarada-hbegajbsfxekdyex.canadacentral-01.azurewebsites.net"

def test_endpoint(url, method="GET", data=None, print_response=True, headers=None):
    """Test a specific endpoint URL and print the results."""
    if headers is None:
        headers = {"Content-Type": "application/json"}
        
    print(f"\n=== Testing {method} {url} ===")
    
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
    """Run all tests with various URL formats."""
    print(f"Testing Azure backend at: {AZURE_URL}")
    print("Testing multiple URL formats and endpoints to diagnose routing issues.")
    
    # Test root endpoint
    test_endpoint(AZURE_URL)
    
    # Standard API endpoints with normal path
    test_endpoint(f"{AZURE_URL}/api/health")
    test_endpoint(f"{AZURE_URL}/api/posts")
    test_endpoint(f"{AZURE_URL}/api/users")
    
    # Try with different URL formats
    test_endpoint(f"{AZURE_URL}/api")  # Just the /api base path
    
    # Try the root Flask app object path
    test_endpoint(f"{AZURE_URL}/") 
    
    # Try adding app.py explicitly (sometimes helps with certain hosting setups)
    test_endpoint(f"{AZURE_URL}/app.py")
    test_endpoint(f"{AZURE_URL}/app/health")
    
    # Try with query parameters (sometimes affects routing)
    test_endpoint(f"{AZURE_URL}/api/health?check=true")
    test_endpoint(f"{AZURE_URL}/api/posts?limit=10")
    
    # Try without https
    test_endpoint(AZURE_URL.replace("https://", "http://"))
    test_endpoint(AZURE_URL.replace("https://", "http://") + "/api/health")
    
    # Try with trailing slashes
    test_endpoint(f"{AZURE_URL}/api/health/")
    test_endpoint(f"{AZURE_URL}/api/posts/")
    
    # Try posting to an endpoint that should be a GET
    test_endpoint(f"{AZURE_URL}/api/health", method="POST", data={})
    
    # Complete API paths
    endpoints = [
        "/",
        "/api",
        "/api/",
        "/api/health",
        "/api/posts",
        "/api/users",
        "/api/login",
        "/api/register"
    ]
    
    print("\n\n=== Testing all standard API paths ===")
    results = {}
    for endpoint in endpoints:
        url = AZURE_URL + endpoint
        success = test_endpoint(url, print_response=False)
        results[endpoint] = success
    
    # Print a summary
    print("\n=== Path Test Summary ===")
    for endpoint, success in results.items():
        status = "✅ OK" if success else "❌ Failed"
        print(f"{endpoint:<20} : {status}")
    
    print("\n=== Recommendations ===")
    if results.get("/api/health", False) and not results.get("/api/posts", False):
        print("⚠️ The health endpoint works but other API endpoints don't.")
        print("   This suggests a routing configuration issue in the Flask app or Azure configuration.")
        print("   Possible solutions:")
        print("   1. Check app.py for correct route definitions")
        print("   2. Check for any prefix URL configuration in Azure")
        print("   3. Check for Flask routing middleware or decorators affecting paths")
        print("   4. Check if gunicorn is configured with the correct app object")
    elif not results.get("/", False) and not results.get("/api/health", False):
        print("❌ Neither the root nor any API endpoints work.")
        print("   This suggests a more fundamental issue with the application startup or deployment.")
    elif results.get("/", False) and not results.get("/api/health", False):
        print("⚠️ The root endpoint works but API endpoints don't.")
        print("   This suggests a routing issue in the Flask app with /api/* routes.")

if __name__ == "__main__":
    main() 