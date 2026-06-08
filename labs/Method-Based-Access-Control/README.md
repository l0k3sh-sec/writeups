# 📝 Lab: Method-Based Access Control Can Be Circumvented

**Platform:** PortSwigger Web Security Academy

**Difficulty:** Practitioner

**Status:** ✅ Solved

## 🎯 Objective

Logged in as `wiener:peter` (a non-admin user), exploit the method-based access control flaw to promote `wiener` to administrator.

## 🧠 Vulnerability Analysis

The application enforces access control on the `/admin-roles` endpoint by checking the HTTP method. The security filter is explicitly configured to intercept and validate permissions only for `POST` requests. It completely ignores `GET` requests. However, the backend logic processing the upgrade simply reads the `username` and `action` parameters regardless of how they are delivered (body vs. query string). By switching the request method from `POST` to `GET`, a low-privileged user can route entirely around the access control filter.

## 🚀 Exploitation Steps

### Step 1: Understand the Legitimate Flow

To see how the application intends for this to work, I logged in as `administrator:admin`. I navigated to the `/admin` panel and clicked "Upgrade" on the user `carlos`.

This triggered the following request, which I captured in Burp Suite and sent to Repeater:

```http
POST /admin-roles HTTP/2
Host: 0acd001b04496ec881d94dfd0061003c.web-security-academy.net
Cookie: session=PWWMvrur4XtyLpdu8okqBAdQ4YDE7Cb8
Content-Type: application/x-www-form-urlencoded

username=carlos&action=upgrade

```

### Step 2: Grab the Attacker Context (and a Troubleshooting Lesson)

I logged out of the admin account and logged in as the attacker, `wiener:peter`. My goal was to grab `wiener`'s active session cookie.

* ⚠️ **Mistake I Made:** Initially, I grabbed `session=3mn9Wvx8yPGM1IeiAWiD3HaVJ24eUxqu` from my HTTP history. However, looking closer, this cookie was attached to a `GET /logout` request. When a user hits `/logout`, the server destroys that session on the backend. Even though the cookie was still in my browser/Repeater, it was a "dead" cookie. Any request with it would result in a `401 Unauthorized` or a redirect to the login page.
* **The Fix:** I logged back in and grabbed a fresh, active session cookie from a `GET /my-account?id=wiener` request: `session=8s2vBD0CpFt7QS5YZfk27dQNT3g11RQo`.

### Step 3: The Exploit

In the Repeater tab containing the original admin `POST` request, I made the following modifications:

1. Swapped the admin's cookie with `wiener`'s active session cookie (`8s2v...`).
2. Changed the parameter `username=carlos` to `username=wiener`.
3. Right-clicked the request in Burp → selected **Change request method** → converted it from `POST` to `GET`.

Burp automatically moved the body parameters into the URL query string, resulting in this payload:

```http
GET /admin-roles?username=wiener&action=upgrade HTTP/1.1
Host: 0acd001b04496ec881d94dfd0061003c.web-security-academy.net
Cookie: session=8s2vBD0CpFt7QS5YZfk27dQNT3g11RQo

```

### Step 4: Verification

Upon sending the request, the server responded with:

```http
HTTP/1.1 302 Found
Location: /admin

```

The `302` redirect to `/admin` confirmed the action was successful. `wiener` was successfully promoted to an administrator!

---

## 💡 Key Concepts & Takeaways

### Why It Worked: A Breakdown

| Question | Answer |
| --- | --- |
| **Why did `GET` bypass the check?** | The application's security filter was configured to only look for `POST` requests on `/admin-roles`. By using `GET`, the request became invisible to the security filter and passed right through. |
| **Why did the backend process it?** | Backend frameworks often use functions like `request.getParameter()`, which don't differentiate between data in the `POST` body and data in a `GET` query string. It found the required parameters and executed the code. |
| **Why did the `3mn9...` cookie fail?** | That session was associated with a `/logout` request. The server had already invalidated it, rendering the cookie dead. |
| **Why did the `8s2v...` cookie work?** | It was an active session from a fresh login. The server recognized the user as authenticated (even if low-privileged), allowing the backend action to execute since the authorization check was bypassed. |

**The Fix:** Developers must enforce access control based on the **endpoint + the user's privilege level**, never just the HTTP method. The HTTP method should never act as the sole gatekeeper for sensitive actions.
