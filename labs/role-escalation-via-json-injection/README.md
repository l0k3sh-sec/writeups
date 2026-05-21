# Lab: User Role Can Be Modified in User Profile

**Difficulty:** Apprentice | **Category:** Access Control

The goal was to modify my account's `roleid` to `2` to gain access to the admin panel and delete the user `carlos`.



Logged in with `wiener:peter` and navigated to the account page. Captured the `POST /my-account/change-email` request in Burp Suite and sent it to Repeater.
originally:
<img width="1599" height="776" alt="image" src="https://github.com/user-attachments/assets/3e9b71d0-1d6a-413b-92b6-d71d5805a592" />


The request body was JSON — added `"roleid": 2` directly into the JSON body alongside the email parameter:

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
<img width="1602" height="778" alt="image" src="https://github.com/user-attachments/assets/d72a3c8d-a2d0-4042-b9be-7afcb898e6cf" />

Navigated to `/admin`, deleted `carlos` — lab solved.

**Key takeaway:** The server accepted additional parameters in the JSON body without any server-side validation, allowing a regular user to escalate privileges just by injecting `"roleid": 2` into an existing request.
