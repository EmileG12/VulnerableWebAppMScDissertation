# 🚨 Vulnerable Web Application - Security Exercise Sheet

## Overview

Welcome to the **Black Pearl Banking** vulnerable web application! This application has been intentionally designed with security education in mind. You are tasked with several cyber security exercises to complete on this bank's simulated web application. See if you can complete these exercises without hints !

⚠️ **WARNING**: This application contains real security vulnerabilities. Only use it in a controlled educational environment.

## 🎯 Learning Objectives

By completing these exercises, you will learn to:
- Identify and exploit Cross-Site Request Forgery (CSRF) attacks
- Perform SQL Injection attacks
- Execute Stored Cross-Site Scripting (XSS) attacks
- Understand Session Hijacking techniques

## 🚀 Getting Started
1. **Access the Application:**
   - Open your browser and go to: `http://localhost:5000`

3. **Default Credentials:**
   - Username: `Johnnydepp` Password: `Pirates`

---

## 📝 Exercise 1: Cross-Site Request Forgery (CSRF)

### What is CSRF?
**Cross-Site Request Forgery (CSRF)** is an attack that tricks a victim into executing unwanted actions on a web application where they're authenticated. The attack works by exploiting the trust that a web application has in the user's browser. When a user is logged into a web application, their browser automatically includes session cookies with every request to that domain. An attacker can craft malicious requests that appear to come from the legitimate user. For example, a bank website could require your session cookie in order to change your password. Without CSRF protection, an attacker could have a form on their website which makes your browser send a request to the bank website with your session cookie. The bank would then receive your cookie and validate the request without your knowledge.

### Question
**Can you delete another user's account without their knowledge using a CSRF attack? Demonstrate how an attacker could craft a malicious webpage that permanently deletes a logged-in user's account when they visit it.**

<details>
<summary>💡 <strong>Hint 1</strong> (Click to expand)</summary>

Look for destructive actions in the application that don't require additional confirmation. Notice that:  
- Some endpoints might accept simple GET requests  
- There might be missing CSRF protection tokens  
- The request might be accepted from any origin  

Try examining what happens when you navigate directly to certain URLs while logged in.
</details>

<details>
<summary>💡 <strong>Hint 2</strong> (Click to expand)</summary>

CSRF attacks work by:  
1. Identifying the exact request format (GET/POST, parameters, etc.)  
2. Creating a malicious HTML page that automatically makes the request  
3. Tricking a logged-in user to visit your malicious page  

For GET-based CSRF attacks, you can use simple HTML elements like `<img>` tags or `<iframe>` elements that automatically load URLs.
</details>

<details>
<summary>🔓 <strong>Solution</strong> (Click to expand)</summary>

**Primary Attack Vector: Hidden Form Auto-Submit**  

1. **Analyze the Request:**  
   - Login to the application and examine available actions  
   - Notice that `/deleteuser` permanently deletes the current user's account  
   - The endpoint accepts GET requests without additional confirmation  

2. **Create Malicious HTML:**  
   ```html  
   <!DOCTYPE html>  
   <html>  
   <head><title>Free Gift Card!</title></head>  
   <body>  
       <h1>Congratulations! You've won a $100 gift card!</h1>  
       <p>Loading your prize...</p>  
       
       <!-- Hidden CSRF attack form -->  
       <form id="csrf" action="http://localhost:5000/deleteuser" method="GET" style="display:none;">  
       </form>  
       
       <script>  
           // Auto-submit after page loads  
           document.getElementById('csrf').submit();  
       </script>  
   </body>  
   </html>  
   ```

3. **Execute the Attack:**  
   - Save as `csrf_delete.html`  
   - Have a logged-in user visit this page  
   - The hidden form automatically submits on page load  
   - Their account is permanently deleted without their knowledge  

4. **Why This Attack is Particularly Dangerous:**  
   - **Irreversible**: The account and all associated data are permanently deleted  
   - **Silent**: The user might not immediately realize what happened  
   - **No confirmation**: Account deletion should require explicit user confirmation  

**Why it works:** The application doesn't validate that the request came from its own forms (no CSRF tokens) and accepts destructive GET requests.

**Note:** This application contains other CSRF vulnerabilities in password changes and username modifications if you wish to explore less destructive attack vectors.
</details>

---

## 📝 Exercise 2: SQL Injection

### What is SQL Injection?
**SQL Injection** is a code injection technique that exploits vulnerabilities in an application's database layer. It occurs when user input is directly inserted into SQL queries without proper sanitization or parameterization. Attackers can manipulate SQL queries to access, modify, or delete data they shouldn't have access to. This can lead to unauthorized data disclosure, data corruption, or even complete database compromise.

### Question
**Can you extract sensitive information from the database using SQL injection? Try to retrieve data from tables you shouldn't have access to, or bypass authentication mechanisms.**

<details>
<summary>💡 <strong>Hint 1</strong> (Click to expand)</summary>

Look for input fields that might be directly inserted into SQL queries without proper sanitization. Common vulnerable endpoints include:  
- Login forms  
- Search functionality  
- User profile updates  
- Credit/account details pages  

Try entering SQL metacharacters like single quotes (`'`) to see if you get database errors.
</details>

<details>
<summary>💡 <strong>Hint 2</strong> (Click to expand)</summary>

SQL Injection techniques to try:  
- **Union-based**: Use `UNION SELECT` to combine results from different tables  
- **Boolean-based**: Use `OR 1=1` conditions to bypass authentication  
- **Error-based**: Use malformed queries to extract database information  

Look at URLs with parameters like `/credit/1` - can you manipulate the `1` to inject SQL?
</details>

<details>
<summary>🔓 <strong>Solution</strong> (Click to expand)</summary>

**Primary Attack Vector: Union-Based SQL Injection via Credit Page**  

1. **Identify the Vulnerable Endpoint:**  
   - Navigate to `/credit/1` (or any user's credit page)  
   - Notice the URL parameter directly reflects in the database query  

2. **Test for Vulnerability:**  
   - Try: `http://localhost:5000/credit/1'`  
   - If you see a database error, the endpoint is vulnerable  

3. **Exploit with Union Select:**  
   ```  
   http://localhost:5000/credit/1 UNION SELECT username,password,userhash,name FROM user--  
   ```  

4. **What happens:**  
   - The malicious SQL gets executed: `SELECT * FROM credit WHERE userid=1 UNION SELECT username,password,userhash,name FROM user--`  
   - This returns both credit data AND all user credentials  
   - You'll see usernames and passwords displayed on the credit page  

5. **Extract Different Data:**  
   ```  
   http://localhost:5000/credit/1 UNION SELECT userid,creditcard,cvv,exp FROM credit--  
   ```  

**Why it works:** The application constructs SQL queries through string concatenation: `SELECT * FROM credit WHERE userid=` + user_input, allowing attackers to inject arbitrary SQL code.  

**Note:** This application has other SQL injection points in the login form and username change functionality if you wish to explore authentication bypass and other attack vectors.  
</details>

---

## 📝 Exercise 3: Stored Cross-Site Scripting (XSS)

### What is Stored XSS?
**Stored Cross-Site Scripting (XSS)** is a vulnerability where malicious JavaScript code is permanently stored on the target server (in a database, file system, or other storage). When other users access the affected page, the malicious script executes in their browser. This is particularly dangerous because it affects every user who views the compromised content, not just the attacker. Stored XSS can be used to steal cookies, hijack sessions, deface websites, or redirect users to malicious sites.

### Question
**Can you inject malicious JavaScript code that will execute when other users view your profile? Demonstrate how an attacker could steal user session cookies through stored XSS.**

<details>
<summary>💡 <strong>Hint 1</strong> (Click to expand)</summary>

Look for input fields where user data gets stored and then displayed to other users. Common locations include:  
- User profiles  
- Display names  
- Comments or posts  
- Any field that appears on pages viewed by others  

The key is finding where input is stored in the database and later displayed without proper HTML escaping.
</details>

<details>
<summary>💡 <strong>Hint 2</strong> (Click to expand)</summary>

XSS payloads to try:  
- **Basic**: `<script>alert('XSS')</script>`  
- **Image tag**: `<img src="x" onerror="alert('XSS')">`  
- **SVG**: `<svg onload="alert('XSS')">`  

Look at the "Update Account Settings" page - there might be different fields for username vs display name. The display name field might be more vulnerable since it's shown on the profile page.
</details>

<details>
<summary>🔓 <strong>Solution</strong> (Click to expand)</summary>

**Primary Attack Vector: Display Name Field XSS**

1. **Identify Vulnerable Field:**  
   - Login to the application
   - Navigate to "Update Account Settings"
   - The **"Change Display Name"** field stores data that appears on the profile page

2. **Test Basic XSS:**  
    - Enter the following in the **"Change Display Name"**  
   ```  
   <script>alert('XSS Attack Successful!')</script>  
   ```  
3. **Verify the attack worked**  
    - Go to the Profile page
    - If an alert pops up, the attack was succesful.  

**Why it works:** The application stores user input and displays it without sanitization which allows JavaScript execution.  

**Note:** This application has other potential XSS vectors in comment fields and other user-controlled content if you wish to explore different injection points.  
</details>

---

## 📝 Exercise 4: Session Hijacking

### What is Session Hijacking?
**Session Hijacking** is an attack where an attacker takes over a user's session by stealing or predicting their session identifier. Web applications use session cookies to maintain user state after authentication. If an attacker can obtain these session cookies, they can impersonate the legitimate user without knowing their credentials. This can happen through various methods including XSS attacks, network sniffing, or exploiting weak session management practices.

### Question
**Can you gain unauthorized access to another user's account by stealing or manipulating their session data? Explore how weak session management can be exploited.**

<details>
<summary>💡 <strong>Hint 1</strong> (Click to expand)</summary>

Session hijacking can occur through various methods:  
- **Cookie theft**: Using XSS to steal session cookies  
- **Session fixation**: Forcing a victim to use a known session ID  
- **Weak session tokens**: Predictable or easily guessable session IDs  

Look at the cookies set by the application when you login. Examine their properties and values using browser Developer Tools → Application → Cookies.
</details>

<details>
<summary>💡 <strong>Hint 2</strong> (Click to expand)</summary>

Check the session implementation:  
- Are session cookies marked as `HttpOnly` and `Secure`?  
- Are session IDs randomly generated or predictable?  
- Can you manually set cookie values to impersonate other users?  

Try logging in as different users and compare their session cookies. Look for patterns in `userid` and `userhash` values. You might be able to craft cookies for other users.  
</details>

<details>
<summary>🔓 <strong>Solution</strong> (Click to expand)</summary>

**Primary Attack Vector: Direct Cookie Manipulation**

1. **Cookie Analysis:**  
   After logging in, examine cookies in Developer Tools (F12 → Application → Cookies):  
   ```  
   userid: 1  
   userhash: 284de456273eafab252a33b59c8de461  
   session: [long_session_string]  
   ```

2. **Test Cookie Manipulation:**  
   - Login as the default user (`Johnnydepp`)  
   - Note your `userid` value (likely `1`, `2`, or `3`)  
   - In the browser console, try changing the userid:  
   ```  
   document.cookie = "userid=2; path=/";  
   location.reload();  
   ```  

3. **Complete Session Hijacking:**  
   - If changing userid alone works, you've successfully hijacked another user's session  
   - You can now access their profile, credit information, and account settings  
   - Try navigating to `/profile` to see the other user's data  

4. **Why This Works:**  
   - The application relies primarily on the `userid` cookie for authentication  
   - No additional session validation is performed  
   - Cookies aren't marked as `HttpOnly` (accessible via JavaScript)  
   - No `Secure` flag means cookies can be transmitted over HTTP  

**Note:** This application has additional session vulnerabilities including predictable userhash patterns and session fixation possibilities if you wish to explore more sophisticated attack vectors.  
</details>

---

## � Advanced Exercise: Multi-Step Account Takeover

### What is Account Takeover?
**Account Takeover** is a sophisticated attack where an attacker gains complete control of another user's account through a combination of reconnaissance, vulnerability exploitation, and credential attacks. This multi-step process involves discovering valid usernames, understanding authentication mechanisms, and either bypassing authorization or cracking passwords. Real-world attackers often chain multiple vulnerabilities together to achieve their goals.

### Multi-Step Challenge
**Can you completely take over another user's account? This requires combining username enumeration, authentication bypass techniques, and password attacks to gain unauthorized access.**

This exercise consists of **two steps** that must be completed in sequence:

#### **Step 1: Username Discovery (Required First)**
Discover valid usernames in the system using the login page's different responses.

#### **Step 2: Account Access (Choose One Path)**
Once you have a username, choose either:
- **Path A**: Authorization bypass through userhash manipulation
- **Path B**: Password cracking using common passwords

---

### **Step 1: Username Enumeration**

<details>
<summary>💡 <strong>Hint 1</strong> (Click to expand)</summary>

The login page provides different error messages or response behaviors for valid vs invalid usernames. This is called "username enumeration."  

Start with your known credentials (`Johnnydepp` / `Pirates`) and observe the application's theme. The application appears to be themed around a famous movie franchise - try other character names from that universe.  
</details>

<details>
<summary>💡 <strong>Hint 2</strong> (Click to expand)</summary>

Pirates of the Caribbean characters to try:  
- Main characters: `Jacksparrow`, `Barbossa`, `Elizabeth`, `Will`  
- Other characters: `Davy`, `Jones`, `Calypso`, `Bootstrap`  

Try these usernames with any password and observe the login response differences between valid and invalid usernames.  
</details>

<details>
<summary>🔓 <strong>Solution</strong> (Click to expand)</summary>

**Username Discovery Process:**  

1. **Analyze Current Credentials:**  
   - You start with: `Johnnydepp` / `Pirates`  
   - Notice the Pirates of the Caribbean theme  

2. **Test Username Enumeration:**  
   - Go to the login page  
   - Try `Jacksparrow` with password `wrongpassword`  
   - Try `InvalidUser` with password `wrongpassword`  
   - Compare the responses - valid usernames will give different error messages  

3. **Discover Valid Usernames:**  
   The following usernames exist in the system:  
   - `Johnnydepp` (already known)  
   - `Jacksparrow`  
   - `Barbossa`  

4. **Confirm Discovery:**  
   - Valid usernames will show "Invalid password" or similar  
   - Invalid usernames will show "User not found" or similar  
   - This difference allows you to enumerate all valid usernames  
   **Result:** You now have valid target usernames: `Jacksparrow` and `Barbossa`  
</details>

---

### **Step 2A: Authorization Bypass**

<details>
<summary>💡 <strong>Hint 1</strong> (Click to expand)</summary>

Examine how the application handles authentication in other pages after you log in. Look at the cookies and form parameters used in requests like `/changepassword`. The application might use predictable session tokens or hashes you can exploit.  

Use Browser Developer Tools to intercept and modify requests. Tools like Burp Suite can also help capture and replay modified requests.  
</details>

<details>
<summary>💡 <strong>Hint 2</strong> (Click to expand)</summary>

The `userhash` parameter in forms might be predictable. Try analyzing a valid request to see if you can determine how a userhash is generated from a username. Then, you might be able to craft valid requests for other users.  

Try using `/changepassword` with a modified `userhash` value.  
</details>

<details>
<summary>🔓 <strong>Solution</strong> (Click to expand)</summary>

**Authorization Bypass via Userhash Manipulation:**  

1. **Capture Legitimate Request:**  
   - Login as `Johnnydepp`  
   - Go to "Update Account Settings"  
   - Open Developer Tools → Network tab  
   - Change your password and capture the `/changepassword` request  

2. **Analyze the Request:**  
   ```  
   POST /changepassword  
   passwordbox=newpass123&userhash=284de456273eafab252a33b59c8de461  
   ```  

3. **Determine Hash Algorithm:**  
   - The userhash appears to be MD5 of the username  
   - Verify: MD5("Johnnydepp") = 284de456273eafab252a33b59c8de461  

4. **Calculate Target Hash:**  
   - For `Jacksparrow`: MD5("Jacksparrow") = 7ce7dce5980b9b01c8d8be2d0f0ae99d  
   - For `Barbossa`: MD5("Barbossa") = 9d3f9b3d0bcef0b8bc1d2d5a5c5e4f1a  

5. **Execute Bypass:**  
   - Use Burp Suite or modify the request manually  
   - Replace the userhash with the target user's hash  
   - Submit: `passwordbox=hacked123&userhash=7ce7dce5980b9b01c8d8be2d0f0ae99d`  
   - You've now changed Jacksparrow's password to "hacked123"  

6. **Verify Access:**  
   - Login as `Jacksparrow` with password `hacked123`  
   - You now have complete access to their account  

**Why it works:** The application trusts the client-provided userhash without proper server-side validation. Since the server does not verify that the hash you provided corresponds to the account you logged in with, it trusts the hash and modifies another account's password.  
</details>

---

### **Step 2B: Password Cracking (Beginner Path)**

<details>
<summary>💡 <strong>Hint 1</strong> (Click to expand)</summary>

Many users choose weak, common passwords. The rockyou.txt wordlist contains millions of commonly used passwords from real data breaches.  

You can download rockyou.txt from security websites or use a smaller common password list. Try passwords related to the Pirates of the Caribbean theme first.  
</details>

<details>
<summary>💡 <strong>Hint 2</strong> (Click to expand)</summary>

Common weak passwords to try:  
- Theme-related: `Blackpearl`, `Princess`, `Caribbean`, `Pirate`  
- Simple passwords: `password`, `123456`, `admin`, `qwerty`  
- Character names: `Elizabeth`, `Bootstrap`, `Calypso`  

Use Burp Suite's Intruder feature to automate password attempts, or try them manually.  
</details>

<details>
<summary>🔓 <strong>Solution</strong> (Click to expand)</summary>

**Password Cracking Attack:**  

1. **Prepare Password List:**  
   - Download rockyou.txt or create a custom list
   - Pirates-themed passwords to try first:    
     Blackpearl  
     Princess  
     Caribbean  
     Pirate  
     Bootstrap  
     Elizabeth  
     Calypso    

2. **Automated with Burp Suite:**  
   - Capture a failed login request  
   - Send to Intruder  
   - Set payload position on the password field  
   - Load your password list  
   - Start attack and look for different response lengths/codes  

4. **Discovered Credentials:**  
   - `Jacksparrow` / `Blackpearl`  
   - `Barbossa` / `Blackpearl`  

5. **Verify Access:**  
   - Login with the discovered credentials  
   - Access their profiles, credit information, and account settings  

**Why it works:** Users often choose predictable, personally relevant passwords or very common passwords that appear in common password lists.  
</details>

---

## 📊 **Exercise Summary**

After completing this multi-step exercise, you will have:

1. **Discovered valid usernames** through enumeration techniques
2. **Gained unauthorized access** through either:
   - Advanced: Authorization bypass via hash manipulation
   - Beginner: Password cracking with common passwords
3. **Demonstrated real-world attack chains** that combine multiple vulnerabilities

This exercise shows how attackers chain multiple techniques together to achieve account takeover - a critical security concern in modern applications.

---

## 🎯 Security Lessons Learned

After completing these exercises, you should understand:

### **CSRF Prevention:**
- Always use CSRF tokens
- Validate the `Referer` header
- Use `SameSite` cookie attributes
- Require re-authentication for sensitive actions

### **SQL Injection Prevention:**
- Use parameterized queries/prepared statements
- Input validation and sanitization
- Principle of least privilege for database accounts
- Regular security code reviews

### **XSS Prevention:**
- Output encoding/escaping
- Content Security Policy (CSP)
- Input validation
- Use frameworks with built-in XSS protection

### **Session Security:**
- Use `HttpOnly` and `Secure` cookie flags
- Implement proper session rotation
- Use cryptographically secure session IDs
- Set appropriate session timeouts
- Validate session integrity

### **Account Takeover Prevention:**
- **Username Enumeration**: Return identical responses for valid/invalid usernames
- **Authorization Controls**: Never trust client-provided session tokens or hashes
- **Password Policy**: Enforce strong passwords and prevent common/themed passwords
- **Rate Limiting**: Implement account lockout after failed attempts
- **Multi-Factor Authentication**: Require additional verification beyond passwords

---

## 📚 Further Reading

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
