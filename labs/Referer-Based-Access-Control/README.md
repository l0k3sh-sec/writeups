📝 Lab: Referer-Based Access Control
Platform: PortSwigger Web Security Academy

Difficulty: Practitioner

Status: Solved (Speedrun: < 1 min)

🎯 Objective
Exploit flawed access controls to promote the wiener user to an administrator.

🧠 Vulnerability Analysis
The application attempts to secure the /admin-roles endpoint by checking the Referer HTTP header. The backend logic essentially asks: "Did this request originate from the /admin page?" instead of asking the correct security question: "Is the user making this request actually an administrator?" Because HTTP headers are entirely client-controlled, this check is easily bypassed. By sending a request with a spoofed Referer header pointing to /admin (or simply reusing a captured request that already has it), a low-privileged user can execute high-privileged actions.

🚀 Exploitation Steps
Step 1: Capture the Intended Admin Request
First, I logged in with the provided administrator credentials (administrator:admin) to understand the normal workflow.

Navigated to the Admin Panel.

Clicked "Upgrade" on the user carlos.

Intercepted the resulting GET request in Burp Suite and sent it to Repeater:

HTTP
GET /admin-roles?username=carlos&action=upgrade HTTP/2
Host: 0ac800a60469e95180d835ec00ad00ba.web-security-academy.net
Cookie: session=OCOKLk66KAdFm3S29UjqzS3LPq9LfxuV
Referer: https://0ac800a60469e95180d835ec00ad00ba.web-security-academy.net/admin
...
(Notice the Referer header is naturally set to the /admin page).

Step 2: Grab the Attacker Context
In a new browser tab, I logged in using the attacker credentials (wiener:peter). I checked my HTTP history to grab wiener's active session cookie.

Step 3: The Exploit
Back in Repeater, I modified the captured admin request with two simple changes:

Replaced the admin's session cookie with wiener's session cookie.

Changed the username parameter in the URL from carlos to wiener.

HTTP
GET /admin-roles?username=wiener&action=upgrade HTTP/2
Host: 0ac800a60469e95180d835ec00ad00ba.web-security-academy.net
Cookie: session=[WIENER_SESSION_COOKIE]
Referer: https://0ac800a60469e95180d835ec00ad00ba.web-security-academy.net/admin
...
Step 4: Verification
I sent the request. Because the request still contained the Referer: .../admin header from my original capture, the server's flawed access control check passed. The server returned a 302 Found response, successfully upgrading wiener to administrator status.

📓 Referer-Based Access Control
Concept Overview:

The Vulnerability: Relying on the Referer header to authenticate or authorize a request.

The Fix: Access control must always be validated on the backend against the user's actual session/privilege level, never by trusting client-provided headers.

Why this lab felt "too easy":

The server was checking the Referer to see if it contained /admin.

Because my methodology involves capturing the original admin request and modifying it, the correct Referer was already in the request. I got it for free!

It felt like there was no check at all, but the check was just inherently bypassed by my workflow.

Proof: If I had sent that exact same request as wiener but deleted the Referer header entirely, the server would have thrown a 403 Unauthorized.

Key Takeaway for Bug Bounty:
When testing administrative actions, always try stripping out or modifying headers like Referer or Origin. If an action succeeds with the header but fails without it (or with a modified one), you've found a vulnerability in how the backend validates authorization.
