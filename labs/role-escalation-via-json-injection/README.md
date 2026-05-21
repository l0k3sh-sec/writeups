# Lab: User Role Can Be Modified in User Profile

**Difficulty:** Apprentice | **Category:** Access Control

The goal was to modify my account's `roleid` to `2` to gain access to the admin panel and delete the user `carlos`.

Logged in with `wiener:peter` and navigated to the account page. Captured the `POST /my-account/change-email` request in Burp Suite and sent it to Repeater. The request body was JSON — added `"roleid": 2` directly into the JSON body alongside the email parameter:

```json
{"email": "wiener1@normal-user.net", "roleid": 2}
```

Server responded with the updated account object confirming the role change:

```json
{
  "username": "wiener",
  "email": "wiener1@normal-user.net",
  "apikey": "W36hgDTtPG9fEnkpRM9KeXX8ENgrFjGH",
  "roleid": 2
}
```

Navigated to `/admin`, deleted `carlos` — lab solved.

**Key takeaway:** The server accepted additional parameters in the JSON body without any server-side validation, allowing a regular user to escalate privileges just by injecting `"roleid": 2` into an existing request.
