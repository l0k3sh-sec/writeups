# 📝 Lab: Username Enumeration via Response Timing

**Platform:** PortSwigger Web Security Academy

**Difficulty:** Practitioner

**Status:** ✅ Solved

**Topic:** Authentication

**Tags:** `#authentication` `#username-enumeration` `#response-timing` `#brute-force` `#x-forwarded-for` `#ip-bypass` `#portswigger` `#burp-intruder`

## 🎯 Objective

Enumerate a valid username by exploiting response time differences, then brute-force the password—all while bypassing IP-based brute-force protection using HTTP headers.

## 🧠 Vulnerability Analysis

The login endpoint is vulnerable to a response timing attack. When a valid username is submitted, the server processes the password verification (hashing and comparing), which causes a measurable delay. If an invalid username is submitted, the server rejects it immediately without checking the password.

Additionally, the server implements IP-based rate limiting (blocking users for 30 minutes after two failed attempts). However, this protection blindly trusts the `X-Forwarded-For` HTTP header, allowing an attacker to bypass the block by spoofing a new IP address for every request.

## 🚀 Exploitation Steps

### Step 1: Baseline Testing & Amplifying the Signal

Before using Intruder, I manually tested the target in Burp Repeater to understand the server's behavior.

* Tried `test:test1` ➔ Response time ~493ms (normal rejection).
* Tried `wiener:test1` (known valid user) ➔ Similar response time. The password was too short to create a noticeable latency gap.

**The Insight:** To amplify the timing signal, I crafted an excessively long password: `test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1`.

* Tried `wiener` + long password ➔ Response time spiked to **877ms**.
* Tried invalid user + long password ➔ Response time remained low.

This confirmed the server only hashes and checks the password if the username exists in the database.

### Step 2: Discovering and Bypassing the IP Block

During manual testing, the server started rejecting requests instantly, returning a message about being blocked. Research indicated this is a standard IP-based block after repeated failed attempts.

* **The Bypass:** I added the `X-Forwarded-For` header to trick the server into thinking the request originated from a different client.
```http
X-Forwarded-For: 192.168.111.11

```


* The server accepted the request as a fresh IP. Bypass confirmed.

### Step 3: Username Enumeration (Intruder)

To find the valid target username, I sent the request to Intruder and configured a **Pitchfork** attack.

* **Payload 1 (IP Spoofing):** Placed a marker in the `X-Forwarded-For` header (`192.168.0.§1§`) and used a Numbers payload (1–103).
* **Payload 2 (Username):** Placed a marker on the username parameter (`username=§peter§`) and loaded the provided wordlist.
* **Body:** Hardcoded the massive password to guarantee a high response time on a hit.

> **Crucial Setting:** I enabled the *Response Completed* column in Intruder (via the 3-dot menu) and restricted the attack to **1 concurrent thread** to prevent network jitter from skewing the timing data.

**Result:** The username `azureuser` returned a response time of ~884ms, drastically higher than the rest. I verified this manually in Repeater with a fresh IP, confirming it was the valid target.

### Step 4: Password Brute-Force (Intruder)

With the username confirmed, I set up a second Pitchfork attack to find the password.

* **Payload 1 (IP Spoofing):** Number list from 106–210 (using a fresh range to avoid hitting my previous blocks).
* **Payload 2 (Password):** Loaded the provided password wordlist.
* **Body:** `username=azureuser&password=§peter§`

**Result:** The payload `pepper` returned a `302 Found` status code, indicating a successful login redirect.

### Step 5: Final Execution & Login

When I attempted to log into the browser normally with `azureuser:pepper`, I was blocked because my actual machine's IP was still in the 30-minute cooldown penalty box.

* **The Fix:** I intercepted the browser's login request in Burp, injected `X-Forwarded-For: 192.168.99.99`, and forwarded it. The server accepted the spoofed IP, granted the session cookie, and the lab was solved.

---

## 🛑 Mistakes & Troubleshooting

1. **Measuring the Wrong Metric:** Early on, I looked at *response length* instead of *timing*, leading me to false positives like "analyzer" and "admin".
2. **Weak Timing Signals:** Using a short password initially resulted in a negligible time difference (20-30ms). Utilizing a massive password was necessary to force the server to work harder and make the latency obvious (400ms+ difference).
3. **Hidden Burp Columns:** I initially relied on *Response Received* (first byte). The true timing difference is measured in *Response Completed* (full response), which must be manually enabled in Intruder.
4. **IP Pool Exhaustion:** During the password brute-force phase, I accidentally reused the same IP number range (1-103) from the username phase, resulting in blocks. I had to shift to a fresh block (106-210).
---

## 💡 Key Concepts

| Concept | Explanation |
| --- | --- |
| **Response Timing Attack** | Exploiting server behavior by measuring how long it takes to process different inputs to infer backend data (like valid users). |
| **Long Password Amplification** | Intentionally sending a massive password string to force the server's hashing algorithm to consume more CPU cycles, thereby amplifying the timing difference. |
| **X-Forwarded-For Spoofing** | Abusing an HTTP header designed for proxies to trick the application into logging/restricting a forged IP address instead of the actual attacker's IP. |
| **Single-Threaded Intruder** | When conducting timing attacks, parallel requests will skew network latency. Attacks must be run on a single thread to maintain accurate baseline timing. |
