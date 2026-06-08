# 📝 Lab: Username Enumeration via Subtly Different Responses

**Platform:** PortSwigger Web Security Academy

**Status:** ✅ Solved

**Topic:** Authentication

**Tags:** `#auth` `#username-enumeration` `#burp-intruder` `#grep-extract`

## 🎯 Objective

Enumerate a valid username by detecting a subtle difference in error messages, then brute-force the correct password to gain account access.

## 🧠 Vulnerability Analysis

Applications should ideally return identical, generic error messages for both invalid usernames and invalid passwords (e.g., "Invalid username or password."). However, in this lab, a tiny typographical error in the backend code causes the error message for a *valid* username (with an invalid password) to be subtly different.

Specifically, the period at the end of the sentence is missing. This single-character difference is practically invisible when rendered in a web browser, but it can be easily detected by analyzing the raw HTML responses using Burp Suite's Grep Extract feature.

## 🚀 Exploitation Steps

### Step 1: Setup and Baseline

1. Connected the browser to Burp Suite and navigated to the target login page.
2. Submitted a baseline request with random credentials (`wiener:peter`).
3. Captured the `POST /login` request in the HTTP History and sent it to **Intruder**.

### Step 2: The Rabbit Hole (Response Lengths)

Initially, I attempted to identify the username by looking for anomalies in the response lengths.

1. Set the payload position to the `username` parameter and used the **Sniper** attack type.
2. Loaded the provided username wordlist and ran the attack.
3. **Observation:** One username (`am`) returned a response length of ~900, while all others were ~600.
4. **Result:** I tried brute-forcing passwords for the user `am`, which yielded two passwords with higher response lengths (~2000+), but the login still failed. Relying purely on response length was not reliable enough for this specific application.

### Step 3: Username Enumeration (Grep Extract)

Realizing response lengths were a false flag, I pivoted to inspecting the actual error messages.

1. In Intruder, navigated to **Settings → Grep - Extract → Add**.
2. Triggered a sample request to fetch the HTML response.
3. Highlighted and extracted the exact error message string: `"Invalid username or password."`
4. Ran the Sniper attack again with the username wordlist. Burp now populated a new column showing the exact error string for every request.

**Detection Logic:**

* **Most responses:** `"Invalid username or password."` *(with a period)*
* **One anomalous response (`americas`):** `"Invalid username or password"` *(missing the period)*
  <img width="1568" height="712" alt="image" src="https://github.com/user-attachments/assets/2a950166-f13b-422d-a563-448ed7f76717" />


That missing period confirmed that `americas` was a valid username in the database.

### Step 4: Password Brute Force

With the username confirmed, I moved on to standard password brute-forcing.

1. Hardcoded the username as `americas` in the request.
2. Set the payload marker on the `password` parameter.
3. Loaded the provided password wordlist and ran a Sniper attack.
4. Monitored the **Status Code** column for changes.
   <img width="1568" height="746" alt="image" src="https://github.com/user-attachments/assets/e08c4cfb-ef40-42ef-b3db-413b080ea4db" />


**Detection Logic:**

* **Most responses:** `200 OK` (Login failed, served the login page again).
* **One response (`love`):** `302 Found` (Redirected to the user account page).

## 🏆 Final Result

* **Target Username:** `americas`
* **Target Password:** `love`
* **Outcome:** Successfully logged into the target account via the 302 redirect and solved the lab.

---

## 💡 Key Concepts & Takeaways

* **Visual Invisibility:** Vulnerabilities like this prove why you cannot rely solely on the browser UI for bug bounty hunting. A missing period is impossible to spot visually but stands out immediately in raw HTTP analysis.
* **The Power of Grep Extract:** When payload responses don't show obvious status code or length differences, `Grep Extract` is the best tool to map out exact behavioral differences in how the server reflects text.
* **Always Verify Anomalies:** My initial finding based on response length (`am`) was a false positive. Always verify your enumerated targets before committing to a full brute-force attack on the next step.
