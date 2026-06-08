# 📝 Lab: Username Enumeration via Account Lock

**Platform:** PortSwigger Web Security Academy

**Difficulty:** Practitioner

**Status:** ✅ Solved

**Topic:** Authentication

**Tags:** `#authentication` `#account-lock` `#username-enumeration` `#logic-flaw` `#grep-extract`

## 🎯 Objective

Enumerate a valid username by triggering an account lockout, then brute-force the password by exploiting a logic flaw in how the lockout state is applied.

## 🧠 Vulnerability Analysis

The application has two distinct vulnerabilities:

1. **Username Enumeration:** The login form locks an account after several failed attempts. The message for a locked account differs from the generic "Invalid username or password" error. Because invalid usernames never lock (they don't exist), this difference leaks which usernames are valid.
2. **Logic Flaw (Authentication Bypass):** The server checks if the submitted password is correct *before* it enforces the lockout response. Therefore, submitting the correct password bypasses the locked state entirely.

## 🚀 Exploitation Steps

### Step 1: Build an Expanded Username List

To guarantee we hit the lockout threshold (usually 3-5 attempts) for any valid user, I used a bash script to generate a wordlist where every username repeats 5 times sequentially:

```bash
while read user; do
    for i in {1..5}; do
        echo "$user"
    done
done < usernames.txt > expanded_usernames.txt

```

*(Result: `carlos`, `carlos`, `carlos`... `peter`, `peter`...)*

### Step 2: Username Enumeration

1. Captured a `POST /login` request in Burp HTTP History and sent it to **Intruder**.
2. Set the payload position on the `username` parameter and used the **Sniper** attack mode.
3. Loaded `expanded_usernames.txt` and ran the attack, monitoring the **Length** column.

**Detection Logic:**

* **Most responses:** Length `3158` ➔ *"Invalid username or password."*
* **One outlier (`guest`):** Length `3288` ➔ *"You have made too many incorrect login attempts. Please try again in 1 minute(s)."*
  <img width="1536" height="781" alt="image" src="https://github.com/user-attachments/assets/70150067-0353-4349-b370-2e4c442d7afd" />


The presence of the lockout message confirmed that `guest` was a valid user in the database.

### Step 3: Reasoning Through the Lock Problem

Now that `guest` was confirmed, the account was locked.

* *Thought process:* Could I use `X-Forwarded-For`?
* *Correction:* No. IP blocking targets the visitor's machine. Account locking freezes the account record in the database itself. Changing my IP would do nothing.
* *Hypothesis:* "Is there any password that returns a different response, even while the account is locked?"

### Step 4: Password Brute Force (Exploiting the Logic Flaw)

1. Hardcoded the username as `guest` in Intruder.
2. Set the payload position on the `password` parameter.
3. Loaded the provided password wordlist.
4. Configured **Grep - Extract** to target the error message: *"You have made too many incorrect login attempts."*
5. Ran the Sniper attack.

**Detection Logic:**

* **Most responses:** Grep Extract showed the lockout error or the invalid credentials error.
* **One response (`7777777`):** Grep Extract returned a blank string (or grabbed the underlying `<form>` HTML).
<img width="1526" height="762" alt="image" src="https://github.com/user-attachments/assets/6d934c09-61fb-4d6e-b0c4-fac52df23764" />


**The "Aha!" Moment:** Because the password was correct, the server did *not* generate an error message. Burp's Grep Extract couldn't find the `<p class='is-warning'>` tag, which made this payload stand out immediately.

### Step 5: Wait and Login

1. Waited 1 minute for the account lockout timer to expire.
2. Logged in manually via the browser using `guest:7777777`.
3. Successfully accessed the account page.

---

## 🛑 Debugging & The Logic Flaw Explained

### How the Logic Flaw Works

The vulnerability stems from the order of operations in the backend code. The server's logic likely looks like this:

1. Receive credentials.
2. **Check if password is correct.**
* If YES ➔ Log user in / Reset failed attempts counter.
* If NO ➔ Check failed attempts counter.
* If Counter > threshold ➔ Show "Locked" message.
* If Counter < threshold ➔ Increment counter, show "Invalid" message.





Because the correctness check happens *first*, a correct password sails right past the lockout enforcement. The account is only "locked" against wrong passwords!

### Mistakes & Confusions

* **Confusing IP Blocks vs. Account Locks:** Initially considered `X-Forwarded-For`, but successfully reasoned my way out of that rabbit hole by understanding the backend mechanics.
* **Doubting the Brute Force:** I wasn't sure if brute-forcing a locked account would even yield results, but running the attack anyway revealed the logic flaw experimentally.

---

## 💡 Root Cause & Mitigations

### The Root Cause

The developer placed the credential validation step before the account state validation step. The lockout penalty was only applied within the "wrong-password" logic branch, leaving the "correct-password" branch completely unprotected from brute-force discovery.

### Developer Mitigations

* **Enforce State First:** Always check the account's lockout status *before* validating the password.
* **Immediate Rejection:** If an account is locked, the application should reject the request immediately without ever touching the password hashing/comparison functions.
* **Generic Messaging:** Unify error messages. A locked account should ideally throw a generic error, or the application should use CAPTCHAs/time-delays rather than explicit lock warnings that enable username enumeration.
