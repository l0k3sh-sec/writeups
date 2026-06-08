# 📝 Lab: Broken Brute-Force Protection, IP Block

**Platform:** PortSwigger Web Security Academy

**Difficulty:** Practitioner

**Status:** ✅ Solved

**Topic:** Authentication

**Tags:** `#authentication` `#brute-force` `#ip-block` `#logic-flaw` `#burp-intruder` `#pitchfork`

## 🎯 Objective

Exploit a logic flaw in IP-based brute-force protection to brute-force `carlos`'s password, then log in and access their account page.

## 🧠 Vulnerability Analysis

The application implements IP-based brute-force protection, which blocks an IP address after a certain number of failed login attempts. However, there is a critical logic flaw: **the failed attempt counter resets to zero upon any successful login from that IP**. Also all headers for IP forwarding are blocked by Target

This means that if an attacker possesses one set of valid credentials, they can interleave a successful login between every brute-force guess. Because the counter is constantly resetting, the lockout threshold is never reached, effectively neutralizing the brute-force protection.

## 🚀 Exploitation Steps

### Step 1: Capture the Baseline Request

1. Navigated to the `/login` page.
2. Submitted the known valid credentials (`wiener:peter`).
3. Captured the `POST /login` request in Burp's HTTP history and sent it to **Intruder**.
4. Marked both the `username` and `password` parameters as payload positions.

### Step 2: Build Interleaved Wordlists

To exploit the logic flaw, I needed to alternate between a valid login and an invalid guess. I used bash scripting in the terminal to generate two perfectly synced wordlists.

**Username List (`usernames.txt`):**

```bash
for i in {1..100}; do echo "wiener"; echo "carlos"; done > usernames.txt

```

*(Result: `wiener`, `carlos`, `wiener`, `carlos`... repeating)*

**Password List (`interleaved_passwords.txt`):**

```bash
for p in $(cat passwords.txt); do echo "peter"; echo "$p"; done > interleaved_passwords.txt

```

*(Result: `peter`, `candidate1`, `peter`, `candidate2`... repeating)*

### Step 3: Configure Intruder (Pitchfork)

1. Set the Attack Type to **Pitchfork** (which iterates through multiple payload sets simultaneously, line-by-line).
2. **Payload 1 (Username):** Loaded `usernames.txt`.
3. **Payload 2 (Password):** Loaded `interleaved_passwords.txt`.

**The resulting attack flow:**

* **Request 1:** `wiener:peter` *(Valid login ➔ Resets IP block counter)*
* **Request 2:** `carlos:candidate1` *(Brute-force guess)*
* **Request 3:** `wiener:peter` *(Valid login ➔ Resets IP block counter)*
* **Request 4:** `carlos:candidate2` *(Brute-force guess)*

### Step 4: Run Attack & Monitor

I started the attack and monitored the **Status Code** column.

* **200 OK:** Failed login (served the login page again).
* **302 Found:** Successful login redirect.

The payload `131313` returned a `302 Found`, confirming it was the correct password for `carlos`.


## 💡 Root Cause & Mitigations

### The Root Cause

The developer implemented an IP-based lockout but tied the counter reset function to *any* successful login event from that IP. This created a logical loophole where an attacker with a single low-privileged account could keep the counter at zero indefinitely while brute-forcing a completely different account.

### Developer Mitigations

* **Independent Counters:** Never reset the failed attempt counter based on a successful login to a *different* account.
* **Time-Based Cooldowns:** Enforce a strict time-based cooldown that cannot be bypassed or reset by any user action.
* **Account-Level + IP-Level Limits:** Rate limit both the target account (e.g., lock the account after 5 tries) AND the originating IP address.
* **Exponential Backoff:** Increase the wait time exponentially for each subsequent failed attempt from an IP.
* **Pattern Detection:** Flag anomalous authentication flows, such as an IP rapidly alternating logins between two specific usernames.
