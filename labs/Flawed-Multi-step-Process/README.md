# 📝 Lab: Multi-Step Process with No Access Control on One Step

**Platform:** PortSwigger Web Security Academy

**Difficulty:** Practitioner

**Status:** Solved

## 🎯 Objective

The application has an admin panel with a flawed multi-step process for changing a user's role. The goal is to log in as `wiener` and exploit this flawed access control to promote ourselves to an administrator.

## 🧠 Vulnerability Analysis

The core issue in this lab is how the backend handles multi-step processes. The developers correctly implemented access control on the *initial* request to upgrade a user. However, they failed to implement the same authorization checks on the subsequent "Are you sure?" confirmation step. Because the server does not verify if the user submitting the confirmation has the proper permissions, a lower-privileged user can force the upgrade process.

## 🚀 Exploitation Steps

### Step 1: Analyze the Admin Workflow

To understand how the upgrade mechanism works, I initially logged in using the provided administrator credentials (`administrator:admin`).

1. Navigated to the Admin Panel.
2. Initiated an upgrade for the user `carlos`.
3. The application intercepted this and prompted an "Are you sure?" confirmation page.

I captured the confirmation request in Burp Suite, which looked like this:

```http
POST /admin-roles HTTP/2
Host: 0a3600c20428b56f807fb2b300a3006c.web-security-academy.net
Cookie: session=xfX9YormjWC8OAT4vwzT02zk9Hw69OMh
Content-Type: application/x-www-form-urlencoded

action=upgrade&confirmed=true&username=carlos

```

*I sent this request to Repeater for later use.*

### Step 2: Switch to the Target Context

Next, I logged out of the admin account and logged in using the attacker credentials (`wiener:peter`).

* **Note:** It is crucial to grab the correct, active session cookie for `wiener` after a fresh login. I confirmed I had the right session by looking at the `GET /my-account?id=wiener` request in my HTTP history.

### Step 3: The Exploit (and a Quick Mistake)

I went back to my intercepted confirmation request in Repeater. My goal was to change the `username` parameter to `wiener` and send it.

**The Mistake:** At first, I changed the payload to `action=upgrade&confirmed=true&username=wiener`, but I forgot to actually paste `wiener`'s session cookie into the header! I only highlighted the old admin cookie but didn't replace it, causing the request to fail. Always double-check your headers!

**The Fix:** I grabbed `wiener`'s session cookie again (`session=l4gw7HVirKn2BAihY0X7yNwOOHYgzVpE`) and successfully pasted it into the intercepted POST request.

The final, winning payload looked like this:

```http
POST /admin-roles HTTP/2
Host: 0a1400ed0400179480a4a38f0018009f.web-security-academy.net
Cookie: session=l4gw7HVirKn2BAihY0X7yNwOOHYgzVpE
Content-Type: application/x-www-form-urlencoded

action=upgrade&confirmed=true&username=wiener

```

### Step 4: Verification

Upon sending the request, the server responded with a `302 Found` status code. This redirect confirmed that the action was successful and `wiener` had been upgraded to an administrator.

## 💡 Author's Note

This was my first Practitioner-level lab that I solved completely without any external help or clues! It took very little time to identify the vulnerability using the context from previous labs. The biggest takeaway here is that developers must enforce strict authentication and authorization checks on *every single step* of a multi-step function, not just the entry point.
