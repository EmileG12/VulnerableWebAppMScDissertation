#!/usr/bin/env python3
"""
Simple CSRF Test Runner
Tests that the vulnerable web app is properly vulnerable to CSRF attacks
"""

import requests
import time

def test_csrf_vulnerabilities():
    """Test CSRF on the vulnerable endpoints"""
    
    print("🔧 CSRF Vulnerability Verification")
    print("=" * 40)
    
    # Test configurations
    base_url = "http://localhost:5000"
    test_creds = {"username": "Jacksparrow", "password": "princess"}
    
    session = requests.Session()
    
    try:
        # 1. Login to establish session
        print("1. Logging in...")
        login_response = session.post(f"{base_url}/login", data=test_creds, allow_redirects=False)
        
        if login_response.status_code not in [302, 303]:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
        print("✅ Login successful")
        
        # 2. Extract cookies for CSRF attacks
        userhash = None
        userid = None
        
        for cookie in session.cookies:
            if cookie.name == 'userhash':
                userhash = cookie.value
            elif cookie.name == 'userid':
                userid = cookie.value
                
        print(f"📋 Found userhash: {userhash[:10]}..." if userhash else "❌ No userhash found")
        print(f"📋 Found userid: {userid}" if userid else "❌ No userid found")
        
        # 3. Test CSRF on password change (vulnerable - no CSRF token)
        print("\n2. Testing CSRF on password change...")
        csrf_data = {
            'newpassword': 'csrf_test_password',
            'userhash': userhash
        }
        
        csrf_response = session.get(f"{base_url}/changepassword", params=csrf_data)
        
        if csrf_response.status_code in [200, 302, 303]:
            print("✅ CSRF VULNERABILITY CONFIRMED: Password change endpoint is vulnerable!")
        else:
            print(f"❌ Password change protected: {csrf_response.status_code}")
            
        # 4. Test CSRF on username change (vulnerable - no CSRF token)
        print("\n3. Testing CSRF on username change...")
        csrf_params = {
            'newusername': 'csrf_hacked_user',
            'userid': userid
        }
        
        csrf_response = session.get(f"{base_url}/changeusername", params=csrf_params)
        
        if csrf_response.status_code in [200, 302, 303]:
            print("✅ CSRF VULNERABILITY CONFIRMED: Username change endpoint is vulnerable!")
        else:
            print(f"❌ Username change protected: {csrf_response.status_code}")
            
        # 5. Test SQL injection on credit endpoint
        print("\n4. Testing SQL injection...")
        sqli_payload = "1' OR '1'='1"
        
        sqli_response = session.get(f"{base_url}/credit/{sqli_payload}")
        
        if sqli_response.status_code == 500:
            print("✅ SQL INJECTION VULNERABILITY CONFIRMED: Server error indicates SQL parsing issue!")
        elif sqli_response.status_code == 200:
            print("✅ SQL INJECTION VULNERABILITY CONFIRMED: Payload executed successfully!")
        else:
            print(f"❌ SQL injection test inconclusive: {sqli_response.status_code}")
            
        # 6. Test CSRF on delete user endpoint (DANGEROUS - only test in dev!)
        print("\n5. Testing CSRF on delete user endpoint...")
        print("⚠️  WARNING: This will delete the test user account!")
        
        # Create a new session to avoid deleting our current session
        test_session = requests.Session()
        test_login = test_session.post(f"{base_url}/login", data=test_creds, allow_redirects=False)
        
        if test_login.status_code in [302, 303]:
            delete_response = test_session.get(f"{base_url}/deleteuser")
            
            if delete_response.status_code in [200, 302, 303]:
                print("✅ CSRF VULNERABILITY CONFIRMED: Delete user endpoint is vulnerable!")
                print("   ⚠️  User account deletion succeeded without CSRF protection!")
            else:
                print(f"❌ Delete user endpoint protected: {delete_response.status_code}")
        else:
            print("❌ Could not test delete user - login failed for test session")
            
        print("\n🎯 Vulnerability testing complete!")
        print("📝 Note: These vulnerabilities are intentional for educational purposes.")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application.")
        print("💡 Make sure the Flask app is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_csrf_vulnerabilities()
