#!/usr/bin/env python3
"""
Add Test Post to Azure Database

This script will attempt to create a test post in the database by:
1. First checking the database debug endpoint
2. Attempting to login as admin
3. Creating a test post using the API
"""

import requests
import json
import time

# Azure backend URL
AZURE_URL = "https://sarada-hbegajbsfxekdyex.canadacentral-01.azurewebsites.net"

def request_endpoint(endpoint, method="GET", data=None):
    """Send a request to an endpoint and return the result."""
    url = f"{AZURE_URL}{endpoint}"
    print(f"\n=== {method} {url} ===")
    
    headers = {"Content-Type": "application/json"}
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            print(f"Unsupported method: {method}")
            return None
            
        print(f"Status Code: {response.status_code}")
        print(f"Status Message: {response.reason}")
        
        try:
            json_data = response.json()
            print("Response:")
            print(json.dumps(json_data, indent=2)[:1000] + "..." if len(json.dumps(json_data, indent=2)) > 1000 else json.dumps(json_data, indent=2))
            return json_data
        except:
            print("Raw Response:")
            print(response.text[:500] + ("..." if len(response.text) > 500 else ""))
            return response.text
            
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

def login_as_admin():
    """Login as admin to get a token."""
    print("\n=== Logging in as admin ===")
    login_data = {
        "username": "admin",
        "password": "secure_password123"
    }
    
    result = request_endpoint("/api/login", method="POST", data=login_data)
    
    if isinstance(result, dict) and "token" in result:
        return result["token"]
    else:
        print("❌ Failed to login as admin")
        return None

def create_test_post(token):
    """Create a test post using the API."""
    if not token:
        print("❌ No token available, cannot create post")
        return False
        
    print("\n=== Creating test post ===")
    post_data = {
        "title": f"Test Post {time.time()}",
        "content": "This is a test post created by the diagnostic script."
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    url = f"{AZURE_URL}/api/posts"
    print(f"POST {url}")
    
    try:
        response = requests.post(url, json=post_data, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(json.dumps(result, indent=2))
            return 200 <= response.status_code < 300
        except:
            print(response.text)
            return False
    except requests.RequestException as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function to test the posts API."""
    print("Testing posts API on Azure instance...")
    
    # First, check the debug endpoint to see database status
    debug_info = request_endpoint("/api/debug/database")
    
    # Then check if posts endpoint works
    posts_data = request_endpoint("/api/posts")
    
    # Try to login and create a post
    token = login_as_admin()
    if token:
        create_test_post(token)
        
        # Check posts again
        print("\n=== Checking if post was created ===")
        posts_after = request_endpoint("/api/posts")

if __name__ == "__main__":
    main() 